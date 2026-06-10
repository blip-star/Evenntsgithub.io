#!/usr/bin/env python3
"""Nairobi Events Bot – scrapes local listings and alerts on new events."""

from __future__ import annotations

import json
import re
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

TARGET_COUNTY = "Nairobi"
DAYS_AHEAD = 30
DB_FILE = "events_alerts.db"
TELEGRAM_TOKEN = None
TELEGRAM_CHAT_ID = None

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-KE,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
}

console = Console() if RICH_AVAILABLE else None


def init_db() -> None:
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS sent_events "
        "(event_id TEXT PRIMARY KEY, sent_at TIMESTAMP)"
    )
    conn.commit()
    conn.close()


def already_sent(event_id: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute(
        "SELECT 1 FROM sent_events WHERE event_id = ?", (event_id,)
    ).fetchone()
    conn.close()
    return row is not None


def mark_sent(event_id: str) -> None:
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO sent_events VALUES (?, ?)",
        (event_id, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def now_local() -> datetime:
    return datetime.now()


def normalize_dt(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt


def within_window(dt: datetime, days: int = DAYS_AHEAD) -> bool:
    dt = normalize_dt(dt)
    start = now_local().replace(hour=0, minute=0, second=0, microsecond=0)
    return start <= dt <= start + timedelta(days=days)


def fetch_url(url: str) -> str | None:
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            log(f"Attempt {attempt + 1} failed for {url}: {exc}")
            time.sleep(2)
    return None


def log(message: str) -> None:
    if RICH_AVAILABLE and console:
        console.print(message)
    else:
        print(message)


def parse_month_day_year(text: str) -> datetime | None:
    m = re.search(
        r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2}),?\s+(\d{4})\b",
        text, re.I,
    )
    if not m:
        return None
    for fmt in ("%B %d %Y", "%b %d %Y"):
        try:
            return datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", fmt)
        except ValueError:
            continue
    return None


def parse_relative_date(text: str, base: datetime | None = None) -> datetime | None:
    base = base or now_local()
    if re.search(r"\btomorrow\b", text, re.I):
        return base + timedelta(days=1)

    m = re.search(
        r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+"
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\b",
        text, re.I,
    )
    if m:
        dt = datetime.strptime(f"{m.group(2)} {m.group(3)} {base.year}", "%b %d %Y")
        if dt < base - timedelta(days=1):
            dt = dt.replace(year=base.year + 1)
        return dt

    for name, wd in WEEKDAYS.items():
        if re.search(rf"\b{re.escape(name)}\b", text, re.I):
            ahead = (wd - base.weekday()) % 7 or 7
            return base + timedelta(days=ahead)

    return parse_month_day_year(text)


def extract_json_ld(soup: BeautifulSoup) -> list[Any]:
    blocks = []
    for script in soup.find_all("script", type="application/ld+json"):
        if script.string:
            try:
                blocks.append(json.loads(script.string))
            except json.JSONDecodeError:
                pass
    return blocks


def venue_from_location(loc: Any) -> str:
    if isinstance(loc, str):
        return loc
    if isinstance(loc, dict):
        return loc.get("name") or loc.get("address", {}).get("addressLocality") or "Nairobi"
    return "Nairobi"


def collect_json_ld_events(blocks: list[Any], source: str = "Eventbrite") -> list[dict]:
    events, seen = [], set()

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            if node.get("@type") == "ItemList":
                for item in node.get("itemListElement", []):
                    walk(item.get("item", item))
            elif node.get("@type") == "Event":
                start = node.get("startDate")
                if not start:
                    return
                try:
                    dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                except ValueError:
                    return
                if not within_window(dt):
                    return
                url = node.get("url", "")
                if url in seen:
                    return
                seen.add(url)
                events.append({
                    "title": node.get("name", "Untitled"),
                    "date": normalize_dt(dt).isoformat(),
                    "venue": venue_from_location(node.get("location")),
                    "artists": ["See event page"],
                    "url": url,
                    "source": source,
                })
            else:
                for v in node.values():
                    walk(v)

    walk(blocks)
    return events


def apply_time(text: str, dt: datetime) -> datetime:
    m = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM))", text, re.I)
    if m:
        try:
            t = datetime.strptime(m.group(1).upper(), "%I:%M %p")
            return dt.replace(hour=t.hour, minute=t.minute)
        except ValueError:
            pass
    return dt


def fetch_ticketyetu_playwright() -> list[dict]:
    events = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://ticketyetu.com/events", wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(2000)
        for card in page.locator("div.row").filter(has=page.locator("h6")).all():
            try:
                title = card.locator("h6").first.inner_text(timeout=1000).strip()
                body = card.inner_text(timeout=1000)
                dt = parse_month_day_year(body)
                if not dt or not within_window(dt):
                    continue
                dt = apply_time(body, dt)
                vm = re.search(r"--([^-\n]+)--", body)
                href = card.locator("a").first.get_attribute("href") or ""
                link = href if href.startswith("http") else f"https://ticketyetu.com{href}"
                events.append({
                    "title": title, "date": dt.isoformat(),
                    "venue": vm.group(1).strip() if vm else "Location TBA",
                    "artists": ["Check listing"],
                    "url": link or "https://ticketyetu.com/events",
                    "source": "Ticketyetu",
                })
            except Exception:
                continue
        browser.close()
    return events


def fetch_ticketyetu() -> list[dict]:
    try:
        if PLAYWRIGHT_AVAILABLE:
            events = fetch_ticketyetu_playwright()
            log(f"[green]Ticketyetu[/] (Playwright): {len(events)} events")
            return events
        log("[yellow]Ticketyetu[/]: 0 events (install playwright)")
    except Exception as exc:
        log(f"[red]Ticketyetu error[/]: {exc}")
    return []


def fetch_kenyabuzz() -> list[dict]:
    if not PLAYWRIGHT_AVAILABLE:
        log("[yellow]KenyaBuzz[/]: skipped (requires playwright)")
        return []
    events, seen = [], set()
    url = f"https://www.kenyabuzz.com/events?location={TARGET_COUNTY.lower()}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(3000)
            for card in page.locator("a[href*='/events/']").all()[:40]:
                try:
                    href = card.get_attribute("href") or ""
                    if not href or href in seen:
                        continue
                    seen.add(href)
                    title = card.inner_text(timeout=1000).strip()
                    if len(title) < 4:
                        continue
                    parent_text = card.evaluate(
                        "el => (el.closest('article,.card,.event,li,div')||el.parentElement).innerText"
                    )
                    dt = parse_month_day_year(parent_text) or parse_relative_date(parent_text)
                    if not dt or not within_window(dt):
                        continue
                    link = href if href.startswith("http") else f"https://www.kenyabuzz.com{href}"
                    events.append({
                        "title": title, "date": dt.isoformat(),
                        "venue": TARGET_COUNTY, "artists": ["To be announced"],
                        "url": link, "source": "KenyaBuzz",
                    })
                except Exception:
                    continue
            browser.close()
        log(f"[green]KenyaBuzz[/]: {len(events)} events")
    except Exception as exc:
        log(f"[red]KenyaBuzz error[/]: {exc}")
    return events


def fetch_eventbrite() -> list[dict]:
    html = fetch_url("https://www.eventbrite.com/d/kenya--nairobi/events/")
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    events = collect_json_ld_events(extract_json_ld(soup))
    if events:
        log(f"[green]Eventbrite[/] (JSON-LD): {len(events)} events")
        return events

    seen, events = set(), []
    for link in soup.find_all("a", href=re.compile(r"/e/")):
        try:
            href = link.get("href") or ""
            if not href or href in seen:
                continue
            seen.add(href)
            title = link.get_text(" ", strip=True)
            if len(title) < 5:
                continue
            parent = link.find_parent(["section", "article", "li", "div"])
            text = parent.get_text(" ", strip=True) if parent else ""
            dt = parse_relative_date(text) or parse_month_day_year(text)
            if not dt or not within_window(dt):
                continue
            url = href if href.startswith("http") else f"https://www.eventbrite.com{href}"
            vm = re.search(r"(?:AM|PM)\s+([A-Za-z0-9' .,&-]{3,80})\s+Check ticket", text)
            events.append({
                "title": title, "date": dt.isoformat(),
                "venue": vm.group(1).strip() if vm else "Check Eventbrite",
                "artists": ["See event page"], "url": url, "source": "Eventbrite",
            })
        except Exception:
            continue
    log(f"[green]Eventbrite[/] (links): {len(events)} events")
    return events


def send_telegram(event: dict) -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        dt = datetime.fromisoformat(event["date"])
        msg = (
            f"<b>{event['title']}</b>\n"
            f"📅 <code>{dt.strftime('%a, %b %d · %H:%M')}</code>\n"
            f"📍 {event['venue']}\n"
            f"🎵 {', '.join(event['artists'])}\n"
            f"🔗 <a href=\"{event['url']}\">Tickets</a>\n"
            f"<i>{event['source']}</i>"
        )
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": msg,
                  "parse_mode": "HTML", "disable_web_page_preview": True},
            timeout=10,
        )
    except Exception:
        pass


def render_events_table(events: list[dict]) -> None:
    title = f"Nairobi Events · next {DAYS_AHEAD} days"
    if RICH_AVAILABLE and console:
        console.print(Panel(title, border_style="cyan"))
        table = Table(box=box.ROUNDED, show_lines=True, expand=True)
        table.add_column("When", style="green", width=20)
        table.add_column("Event", style="bold white", ratio=2)
        table.add_column("Venue", style="yellow", ratio=1)
        table.add_column("Source", style="magenta", width=12)
        for ev in sorted(events, key=lambda e: e["date"]):
            dt = datetime.fromisoformat(ev["date"])
            table.add_row(
                dt.strftime("%a %b %d · %H:%M"),
                ev["title"][:70], ev["venue"][:40], ev["source"],
            )
        console.print(table)
        return
    print(f"\n{title}\n" + "=" * len(title))
    for ev in sorted(events, key=lambda e: e["date"]):
        dt = datetime.fromisoformat(ev["date"])
        print(f"{dt.strftime('%a %b %d · %H:%M'):<20} | {ev['title'][:50]} | {ev['venue']} | {ev['source']}")


def dedupe(events: list[dict]) -> list[dict]:
    out = {}
    for ev in events:
        key = (ev["title"].lower(), ev["date"], ev["venue"].lower())
        out.setdefault(key, ev)
    return list(out.values())


def main() -> None:
    init_db()
    log(f"\n[bold cyan]Scanning Nairobi events for the next {DAYS_AHEAD} days...[/]\n")

    all_events = fetch_ticketyetu() + fetch_kenyabuzz() + fetch_eventbrite()
    events = dedupe(all_events)
    log(f"\n[bold]Total unique events:[/] {len(events)}\n")

    new_events = []
    for ev in events:
        eid = f"{ev['title']}_{ev['date']}_{ev['venue']}".replace(" ", "_")
        if already_sent(eid):
            continue
        new_events.append(ev)
        send_telegram(ev)
        mark_sent(eid)

    if new_events:
        render_events_table(new_events)
        for ev in new_events:
            log(f"🔗 {ev['url']}")
    elif events:
        render_events_table(events)
        log("[dim]No new events since last run.[/]")
    else:
        log("[yellow]No events found.[/] pip install playwright && playwright install chromium")

    log(f"\n[bold]Sent {len(new_events)} new alerts.[/]\n")


if __name__ == "__main__":
    main()