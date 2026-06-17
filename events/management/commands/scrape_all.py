from django.core.management.base import BaseCommand
from events.scrapers import eventbrite

class Command(BaseCommand):
    help = 'Run all event scrapers'

    def handle(self, *args, **kwargs):
        self.stdout.write('Scraping Eventbrite...')
        try:
            count = eventbrite.scrape_eventbrite()
            self.stdout.write(self.style.SUCCESS(f'Added/updated {count} events from Eventbrite'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Eventbrite failed: {e}'))
        self.stdout.write(self.style.SUCCESS('All scrapers finished.'))
