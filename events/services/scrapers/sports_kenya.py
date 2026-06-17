from .error_handling import safe_scraper

@safe_scraper("Kenya Rugby")
def fetch_kenya_rugby(days_ahead, county="Nairobi"):
    return []
@safe_scraper("Golf Score Kenya")
def fetch_golf_kenya(days_ahead, county="Nairobi"):
    return []
