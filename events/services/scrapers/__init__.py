from .extra_sources import fetch_egotickets, fetch_mtickets, fetch_mookh, fetch_myjiji, fetch_arena, fetch_allevents, fetch_major_events, fetch_mombasa_events

from .ticketyetu import fetch_ticketyetu
from .kenyabuzz import fetch_kenyabuzz
from .eventbrite import fetch_eventbrite
from .mtickets import fetch_mtickets
from .motorsport_kenya import fetch_rx_motorsport, fetch_kmsf, fetch_my_mrotiee
from .food_events import fetch_ticketsasa_food, fetch_kenyabuzz_food, fetch_geco_tribe
from .sports_kenya import fetch_kenya_rugby, fetch_golf_kenya
from .club_sources import fetch_alcapone, fetch_mookh

from .base import dedupe_events, shared_browser
from .error_handling import safe_scraper, safe_scrape_wrapper

def fetch_all(county, days_ahead, include_social=True):
    with shared_browser() as browser:
        scrapers = [
            (fetch_ticketyetu, "Ticketyetu", (days_ahead, browser, county), {}),
            (fetch_kenyabuzz, "KenyaBuzz", (county, days_ahead, browser), {}),
            (fetch_eventbrite, "Eventbrite", (days_ahead, county), {}),
            (fetch_mtickets, "MTickets (Original)", (days_ahead, county), {}),
            (fetch_rx_motorsport, "RX Motorsport", (days_ahead, county), {}),
            (fetch_kmsf, "KMSF", (days_ahead, county), {}),
            (fetch_my_mrotiee, "My Mrotiee", (days_ahead, county), {}),
            (fetch_ticketsasa_food, "Ticketsasa Food", (days_ahead, county), {}),
            (fetch_kenyabuzz_food, "KenyaBuzz Food", (days_ahead, county), {}),
            (fetch_geco_tribe, "Geco Tribe", (days_ahead, county), {}),
            (fetch_kenya_rugby, "Kenya Rugby", (days_ahead, county), {}),
            (fetch_golf_kenya, "Golf Score Kenya", (days_ahead, county), {}),
            (fetch_alcapone, "Al Capone", (days_ahead, county), {}),
            (fetch_mookh, "Mookh (Club)", (days_ahead, county), {}),
            # New extra sources
            (fetch_egotickets, "eGotickets", (days_ahead, county), {}),
            (fetch_mtickets, "MTickets (Extra)", (days_ahead, county), {}),
            (fetch_mookh, "Mookh (Extra)", (days_ahead, county), {}),
        ]
        events = []
        for func, name, args, kwargs in scrapers:
            events.extend(safe_scrape_wrapper(func, name, *args, **kwargs))
        return dedupe_events(events), []


