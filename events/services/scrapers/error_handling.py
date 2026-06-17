import logging
logger = logging.getLogger(__name__)

def safe_scrape_wrapper(func, source_name, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        logger.info(f"{source_name}: Found {len(result)} events")
        return result
    except Exception as e:
        logger.error(f"{source_name} failed: {e}")
        return []

def safe_scraper(source_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{source_name} failed: {e}")
                return []
        return wrapper
    return decorator
