from django.core.management.base import BaseCommand
from events.services.scanner import generate_mock_events, run_scan

class Command(BaseCommand):
    help = 'Force generate mock events for a county'

    def add_arguments(self, parser):
        parser.add_argument('--county', type=str, default='Nairobi')
        parser.add_argument('--days', type=int, default=30)

    def handle(self, *args, **options):
        scan = run_scan(
            county=options['county'],
            days_ahead=options['days'],
            alert_new_only=True,
            dry_run=False,
            include_social=False
        )
        self.stdout.write(self.style.SUCCESS(f"Generated {scan.events_found} events for {options['county']}"))
