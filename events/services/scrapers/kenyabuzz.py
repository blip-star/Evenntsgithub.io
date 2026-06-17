from .error_handling import safe_scraper

@safe_scraper("KenyaBuzz")
def fetch_kenyabuzz(county, days_ahead, browser=None):
    return []
