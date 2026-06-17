from django.core.management.base import BaseCommand
from events.models import Event
import requests
from bs4 import BeautifulSoup
import re

def fetch_image_from_ticket_url(url):
    if not url or url == '#' or not url.startswith('http'):
        return ''
    try:
        resp = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code != 200:
            return ''
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Try Open Graph
        og = soup.find('meta', property='og:image')
        if og and og.get('content'):
            return og['content']
        # Try Twitter card
        tw = soup.find('meta', attrs={'name': 'twitter:image'})
        if tw and tw.get('content'):
            return tw['content']
        # Try schema.org
        schema = soup.find('meta', attrs={'itemprop': 'image'})
        if schema and schema.get('content'):
            return schema['content']
        # Try first large image
        img = soup.find('img', class_=re.compile(r'poster|event|main|hero|featured', re.I))
        if img and img.get('src'):
            src = img['src']
            if not src.startswith('http'):
                from urllib.parse import urljoin
                src = urljoin(url, src)
            return src
    except:
        pass
    return ''

class Command(BaseCommand):
    help = 'Fetch real event images from ticket URLs'

    def handle(self, *args, **options):
        events = Event.objects.filter(poster_image_url__exact='')
        total = events.count()
        updated = 0
        self.stdout.write(f"Scanning {total} events without images...")
        for ev in events:
            if ev.ticket_url and ev.ticket_url != '#':
                img = fetch_image_from_ticket_url(ev.ticket_url)
                if img:
                    ev.poster_image_url = img
                    ev.save()
                    updated += 1
                    self.stdout.write(f"✓ {ev.title[:50]}")
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} events with real images"))
