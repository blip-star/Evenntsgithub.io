"""
New event sources: eGotickets, Little Events, Tikiti, Instagram hashtags.
All scrapers follow the same pattern and use the safe_scraper decorator.
"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.utils import timezone
from .error_handling import safe_scraper
from ..dates import parse_event_date, apply_time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

@safe_scraper("eGotickets Kenya")
def fetch_egoticketskenya(days_ahead=30, county="Nairobi"):
    """Scrape eGotickets Kenya events."""
    events = []
    url = "https://www.egoticketskenya.com/events"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Adjust selectors based on actual site structure
        for card in soup.select(".event-item, .event-card, .ticket-item"):
            try:
                title = card.select_one("h3, h4, .title").get_text(strip=True)
                date_text = card.select_one(".date, .event-date").get_text(strip=True)
                dt = parse_event_date(date_text)
                if not dt or dt < timezone.now() - timedelta(days=1) or dt > timezone.now() + timedelta(days=days_ahead):
                    continue
                dt = apply_time(date_text, dt)
                venue = card.select_one(".venue, .location").get_text(strip=True) if card.select_one(".venue, .location") else county
                price = card.select_one(".price").get_text(strip=True) if card.select_one(".price") else "TBD"
                link = card.select_one("a").get("href") if card.select_one("a") else ""
                if link and not link.startswith("http"):
                    link = "https://www.egoticketskenya.com" + link
                events.append({
                    "title": title,
                    "date": dt.isoformat(),
                    "venue": venue,
                    "url": link,
                    "source": "eGotickets Kenya",
                    "price": price,
                    "county": county,
                    "image": "",
                    "description": "",
                    "organizer": "",
                })
            except Exception:
                continue
    except Exception as e:
        print(f"eGotickets error: {e}")
    return events

@safe_scraper("Little Events")
def fetch_little_events(days_ahead=30, county="Nairobi"):
    """Scrape Little Events Kenya."""
    events = []
    url = "https://www.littleeventskenya.com/events"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select(".event, .listing, .item"):
            try:
                title = card.select_one(".title, h2, h3").get_text(strip=True)
                date_text = card.select_one(".date, .datetime").get_text(strip=True)
                dt = parse_event_date(date_text)
                if not dt or dt < timezone.now() - timedelta(days=1) or dt > timezone.now() + timedelta(days=days_ahead):
                    continue
                dt = apply_time(date_text, dt)
                venue = card.select_one(".location, .venue").get_text(strip=True) if card.select_one(".location, .venue") else county
                price = card.select_one(".price").get_text(strip=True) if card.select_one(".price") else "TBD"
                link = card.select_one("a").get("href") if card.select_one("a") else ""
                if link and not link.startswith("http"):
                    link = "https://www.littleeventskenya.com" + link
                events.append({
                    "title": title,
                    "date": dt.isoformat(),
                    "venue": venue,
                    "url": link,
                    "source": "Little Events",
                    "price": price,
                    "county": county,
                    "image": "",
                })
            except Exception:
                continue
    except Exception as e:
        print(f"Little Events error: {e}")
    return events

@safe_scraper("Tikiti")
def fetch_tikiti(days_ahead=30, county="Nairobi"):
    """Scrape Tikiti.io events."""
    events = []
    url = "https://tikiti.io/events"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select(".event-card, .card, .event-item"):
            try:
                title = card.select_one("h3, .title").get_text(strip=True)
                date_text = card.select_one(".date, .datetime").get_text(strip=True)
                dt = parse_event_date(date_text)
                if not dt or dt < timezone.now() - timedelta(days=1) or dt > timezone.now() + timedelta(days=days_ahead):
                    continue
                dt = apply_time(date_text, dt)
                venue = card.select_one(".location, .venue").get_text(strip=True) if card.select_one(".location, .venue") else county
                price = card.select_one(".price").get_text(strip=True) if card.select_one(".price") else "TBD"
                link = card.select_one("a").get("href") if card.select_one("a") else ""
                if link and not link.startswith("http"):
                    link = "https://tikiti.io" + link
                events.append({
                    "title": title,
                    "date": dt.isoformat(),
                    "venue": venue,
                    "url": link,
                    "source": "Tikiti",
                    "price": price,
                    "county": county,
                })
            except Exception:
                continue
    except Exception as e:
        print(f"Tikiti error: {e}")
    return events

# Placeholder for Instagram hashtag scraping (requires API)
def fetch_instagram_hashtags(hashtags=["SunsetCorsa", "NairobiEvents"], days_ahead=30):
    """Future: use Instagram Basic Display API or graph API."""
    # This would require OAuth and proper setup.
    # For now, return empty list.
    return []