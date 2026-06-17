import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from events.models import Event
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Scrape events from real sources'

    def add_arguments(self, parser):
        parser.add_argument('--county', type=str, default='Nairobi')
        parser.add_argument('--days-ahead', type=int, default=30)

    def handle(self, *args, **options):
        county = options['county']
        days_ahead = options['days_ahead']
        self.stdout.write(f'Scanning {county} for next {days_ahead} days...')
        
        # For demo: create a sample event if none exists
        if Event.objects.count() == 0:
            Event.objects.create(
                title='Sample: Sunset Corsa',
                date=timezone.now() + datetime.timedelta(days=7),
                venue='Kasarani',
                source='Demo',
                county=county,
                is_recommended=True,
                ai_score=90,
                ai_reason='Demo event'
            )
            self.stdout.write(self.style.SUCCESS('Created demo event'))
        else:
            self.stdout.write(f'Already {Event.objects.count()} events in DB')
