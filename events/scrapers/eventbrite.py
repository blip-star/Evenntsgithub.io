import requests
from events.models import Event
from django.utils import timezone
import hashlib

def scrape_eventbrite(location='Nairobi', days=30):
    api_key = 'YOUR_EVENTBRITE_API_KEY'
    url = f'https://www.eventbriteapi.com/v3/events/search/?location.address={location}&expand=venue'
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for ev in data.get('events', []):
                title = ev.get('name', {}).get('text', '')
                venue = ev.get('venue', {}).get('name', 'Unknown') if ev.get('venue') else 'Unknown'
                date_str = ev.get('start', {}).get('utc')
                if not date_str:
                    continue
                date = timezone.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                poster_url = ev.get('logo', {}).get('url') if ev.get('logo') else ''
                raw = f"{title}|{date.isoformat()}|{venue}".lower()
                event_id = hashlib.sha256(raw.encode()).hexdigest()[:32]
                obj, created = Event.objects.get_or_create(
                    event_id=event_id,
                    defaults={
                        'title': title,
                        'venue': venue,
                        'date': date,
                        'source': 'Eventbrite',
                        'county': 'Nairobi',
                        'poster_image_url': poster_url,
                        'ai_score': 0,
                    }
                )
                if not created and not obj.poster_image_url and poster_url:
                    obj.poster_image_url = poster_url
                    obj.save()
            return len(data.get('events', []))
    except Exception as e:
        print(f"Eventbrite scrape error: {e}")
    return 0
