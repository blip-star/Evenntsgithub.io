from .error_handling import safe_scraper

@safe_scraper("Ticketsasa")
def fetch_ticketsasa(days_ahead, county="Nairobi"):
    return []
