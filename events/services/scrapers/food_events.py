from .error_handling import safe_scraper
from .ticketsasa import fetch_ticketsasa
from .kenyabuzz import fetch_kenyabuzz

@safe_scraper("Ticketsasa Food")
def fetch_ticketsasa_food(days_ahead, county="Nairobi"):
    all_events = fetch_ticketsasa(days_ahead, county)
    return [e for e in all_events if any(k in e.get('title','').lower() for k in ['food','wine','beer','brunch','dinner'])]

@safe_scraper("KenyaBuzz Food")
def fetch_kenyabuzz_food(days_ahead, county="Nairobi"):
    all_events = fetch_kenyabuzz(county, days_ahead)
    return [e for e in all_events if any(k in e.get('title','').lower() for k in ['food','wine','beer','brunch','dinner'])]

@safe_scraper("Geco Tribe")
def fetch_geco_tribe(days_ahead, county="Nairobi"):
    return []
