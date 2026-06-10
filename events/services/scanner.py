from events.services.scrapers import fetch_all
from events.models import ScanRun, Event
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def run_scan(county, days_ahead, alert_new_only, dry_run, include_social,
             enable_ai=True, enable_weather=True, enable_alerts=True, verbose=False):
    scan = ScanRun.objects.create(county=county, days_ahead=days_ahead, scan_type='full' if include_social else 'core')
    try:
        raw, social_posts = fetch_all(county, days_ahead, include_social=include_social)
        scan.events_found = len(raw)
        scan.social_posts_found = len(social_posts)
        # In a real implementation, you would process and save events
        scan.finished_at = timezone.now()
        scan.save()
        logger.info(f"Scan complete: {scan.events_found} events found")
        return scan
    except Exception as e:
        scan.error = str(e)
        scan.finished_at = timezone.now()
        scan.save()
        raise
