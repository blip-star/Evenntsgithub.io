from django.core.management.base import BaseCommand
from events.services.scanner import run_scan

class Command(BaseCommand):
    help = "Scrape events"

    def add_arguments(self, parser):
        parser.add_argument('--county', type=str, default='Nairobi')
        parser.add_argument('--days-ahead', type=int, default=30)
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--include-social', action='store_true')

    def handle(self, *args, **options):
        scan = run_scan(
            county=options['county'],
            days_ahead=options['days_ahead'],
            alert_new_only=True,
            dry_run=options['dry_run'],
            include_social=options['include_social']
        )
        self.stdout.write(self.style.SUCCESS(f"Scanned {scan.events_found} events"))
