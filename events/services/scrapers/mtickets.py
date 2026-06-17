from .error_handling import safe_scraper

@safe_scraper("MTickets")
def fetch_mtickets(days_ahead, county="Nairobi"):
    return []
