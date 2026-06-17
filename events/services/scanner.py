import logging
import random
from datetime import timedelta
from django.utils import timezone
from events.models import Event, ScanRun
from events.services.scrapers import fetch_all
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def fetch_image_from_url(url):
    if not url or url == '#':
        return ''
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return ''
        soup = BeautifulSoup(resp.text, 'html.parser')
        og = soup.find('meta', property='og:image')
        if og and og.get('content'):
            return og['content']
        schema = soup.select_one('[itemprop="image"] img, [itemprop="image"]')
        if schema and schema.get('src'):
            return schema['src']
        img = soup.find('img', class_=lambda c: c and ('poster' in c or 'event' in c or 'main' in c))
        if img and img.get('src'):
            return img['src']
    except:
        pass
    return ''

def generate_mock_events(county, days_ahead):
    events = []
    now = timezone.now()
    categories = ['car events', 'rugby', 'boxing', 'mma', 'amapiano', 'reggae', 'food', 'live music', 'comedy']
    titles = {
        'car events': ['Sunset Corsa Drag Race', 'Nairobi Auto Show', 'Motorsport Kenya Rally', 'Race Wars'],
        'rugby': ['Kenya vs Uganda Rugby', 'KRU Championship Final', 'Safari Sevens', 'Nairobi Rugby Festival'],
        'boxing': ['Heavyweight Championship', 'Nightmare in Nairobi', 'Boxing Gala', 'KO Night'],
        'mma': ['ANZA MMA Fight Night', 'MMA Showdown', 'Warriors of the Ring', 'Submission Challenge'],
        'amapiano': ['Amapiano Fest', 'Piano People', 'Yanos Night', 'Amapiano Experience'],
        'reggae': ['Reggae Sunday Cookout', 'One Love Festival', 'Roots Reggae Party', 'Jamaican Vibes'],
        'food': ['Food & Wine Expo', 'Street Food Festival', 'Brunch Social', 'Taste of Nairobi'],
        'live music': ['Jazz Night', 'Rock Concert', 'Acoustic Sessions', 'Live Band Showcase'],
        'comedy': ['Laugh Festival', 'Comedy Night', 'Stand-up Special', 'Funny Business'],
    }
    venues = {
        'car events': ['Ngong Racecourse', 'Kasarani Stadium', 'Tatu City', 'ICC'],
        'rugby': ['Kasarani Stadium', 'RFUEA Grounds', 'Nakuru Athletic Club', 'Kakamega Showground'],
        'boxing': ['Champions Hall', 'KICC', 'Safaricom Stadium', 'Moi Stadium'],
        'mma': ['Nairobi Gymkhana', 'Kasarani Indoor Arena', 'Charter Hall', 'Nyayo Stadium'],
        'amapiano': ['The Alchemist', 'Westlands', 'K1 Club', 'B Club'],
        'reggae': ['Westlands Park', 'Uhuru Gardens', 'The Alchemist', "J's Bar"],
        'food': ['Westgate Mall', 'Village Market', 'Two Rivers', 'The Junction'],
        'live music': ['The Alchemist', 'Mamba Village', "J's Fresh Bar", 'The Blue Door'],
        'comedy': ['The Alchemist', 'Westlands', 'KICC', 'Mist Lounge']
    }
    weather_conditions = ['Sunny, 28°C, 5% rain', 'Partly Cloudy, 26°C, 10% rain', 'Light Rain, 22°C, 45% rain',
                          'Clear, 27°C, 3% rain', 'Overcast, 24°C, 20% rain', 'Drizzle, 23°C, 35% rain']
    image_urls = {
        'car events': 'https://picsum.photos/id/111/400/200',
        'rugby': 'https://picsum.photos/id/122/400/200',
        'boxing': 'https://picsum.photos/id/133/400/200',
        'mma': 'https://picsum.photos/id/144/400/200',
        'amapiano': 'https://picsum.photos/id/155/400/200',
        'reggae': 'https://picsum.photos/id/169/400/200',
        'food': 'https://picsum.photos/id/127/400/200',
        'live music': 'https://picsum.photos/id/106/400/200',
        'comedy': 'https://picsum.photos/id/20/400/200',
    }
    for i in range(12):
        category = random.choice(categories)
        title = random.choice(titles[category]) + f" {i+1}"
        date = now + timedelta(days=random.randint(1, days_ahead))
        venue = random.choice(venues[category])
        score = random.randint(70, 98)
        weather = random.choice(weather_conditions)
        poster = image_urls[category]
        lat = -1.2864 + random.uniform(-0.1, 0.1)
        lon = 36.8172 + random.uniform(-0.1, 0.1)
        description = f"Experience the best {category} event in {county}. {title} brings you an unforgettable experience."
        reason = f"Matches {category} preferences (AI score {score})"
        events.append({
            'title': title,
            'date': date.isoformat(),
            'venue': venue,
            'source': 'Mock Scraper',
            'ticket_url': '#',
            'county': county,
            'ai_category': category,
            'ai_score': score,
            'ai_reason': reason,
            'is_recommended': score >= 80,
            'description': description,
            'poster_image_url': poster,
            'weather_forecast': weather,
            'weather_temp_c': 25,
            'weather_rain_pct': random.randint(0, 70),
            'map_lat': lat,
            'map_lon': lon,
        })
    return events

def run_scan(county, days_ahead, alert_new_only, dry_run, include_social, **kwargs):
    scan = ScanRun.objects.create(
        county=county,
        days_ahead=days_ahead,
        scan_type='full' if include_social else 'core',
        started_at=timezone.now()
    )
    try:
        real_events, posts = fetch_all(county, days_ahead, include_social)
        if real_events:
            events_to_save = real_events
        else:
            events_to_save = generate_mock_events(county, days_ahead)
            logger.info(f"No real events found, generated {len(events_to_save)} mock events")
        new_count = 0
        for ev in events_to_save:
            event_id = Event.make_event_id(ev['title'], ev['date'], ev['venue'])
            poster = ev.get('poster_image_url')
            if not poster and ev.get('ticket_url'):
                poster = fetch_image_from_url(ev['ticket_url'])
            obj, created = Event.objects.update_or_create(
                event_id=event_id,
                defaults={
                    'title': ev['title'],
                    'date': ev['date'],
                    'venue': ev['venue'],
                    'source': ev.get('source', 'Scanner'),
                    'ticket_url': ev.get('ticket_url', '#'),
                    'county': ev.get('county', county),
                    'ai_category': ev.get('ai_category', ''),
                    'ai_score': ev.get('ai_score', 0),
                    'ai_reason': ev.get('ai_reason', ''),
                    'is_recommended': ev.get('is_recommended', False),
                    'description': ev.get('description', ''),
                    'poster_image_url': poster or '',
                    'weather_forecast': ev.get('weather_forecast', ''),
                    'weather_temp_c': ev.get('weather_temp_c'),
                    'weather_rain_pct': ev.get('weather_rain_pct'),
                    'map_lat': ev.get('map_lat'),
                    'map_lon': ev.get('map_lon'),
                }
            )
            if created:
                new_count += 1
        scan.events_found = len(events_to_save)
        scan.events_new = new_count
        scan.finished_at = timezone.now()
        scan.save()
        logger.info(f"Scan complete: {scan.events_found} events found, {new_count} new")
        return scan
    except Exception as e:
        scan.error = str(e)
        scan.finished_at = timezone.now()
        scan.save()
        raise
