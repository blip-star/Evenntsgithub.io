from .error_handling import safe_scraper

@safe_scraper("Eventbrite")
def fetch_eventbrite(days_ahead, county="Nairobi"):
    return []
