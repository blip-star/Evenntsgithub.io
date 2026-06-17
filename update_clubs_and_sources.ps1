# update_clubs_and_sources.ps1
# =====================================================
$ErrorActionPreference = "Stop"

Write-Host "🚀 Updating Clubs & Sources..." -ForegroundColor Cyan

# 0. Ensure requests is installed
Write-Host "`n📦 Checking dependencies..." -ForegroundColor Yellow
$requests = pip list | Select-String "requests"
if (-not $requests) {
    Write-Host "Installing requests..." -ForegroundColor Yellow
    pip install requests
}

# 1. Add get_weather() to views.py (if missing)
$viewsPath = "events\views.py"
$viewsContent = Get-Content $viewsPath -Raw

if ($viewsContent -notmatch "def get_weather\(") {
    Write-Host "`n🌤️ Adding get_weather() to views.py..." -ForegroundColor Cyan
    $weatherFunc = @"
# =====================================================
# WEATHER HELPER (cached)
# =====================================================
def get_weather(lat, lon):
    \"\"\"Fetch current weather from OpenWeatherMap, cached for 30 minutes.\"\"\"
    if not lat or not lon:
        return None
    cache_key = f'weather_{lat}_{lon}'
    weather = cache.get(cache_key)
    if weather:
        return weather

    api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
    if not api_key:
        return None

    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            weather = {
                'temp': round(data['main']['temp']),
                'condition': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'rain': data.get('rain', {}).get('1h', 0),
            }
            cache.set(cache_key, weather, 60*30)
            return weather
    except Exception as e:
        logger.warning(f"Weather fetch failed: {e}")
    return None
"@
    $newContent = $viewsContent -replace "(import logging.*?)(\n)", "`$1`n$weatherFunc`n`n"
    Set-Content -Path $viewsPath -Value $newContent -Encoding UTF8
    Write-Host "✅ get_weather() added." -ForegroundColor Green
} else {
    Write-Host "⏩ get_weather() already exists." -ForegroundColor Yellow
}

$imports = @"
import requests
from django.core.cache import cache
"@
if ($viewsContent -notmatch "import requests") {
    $newContent = $viewsContent -replace "(import csv.*?)(\n)", "`$1`n$imports`n"
    Set-Content -Path $viewsPath -Value $newContent -Encoding UTF8
    Write-Host "✅ Added requests and cache imports." -ForegroundColor Green
}

# 2. Replace club_list with county/category grouping
Write-Host "`n📋 Updating club_list view..." -ForegroundColor Cyan
$viewsContent = Get-Content $viewsPath -Raw
if ($viewsContent -match "def club_list\(") {
    $viewsContent = $viewsContent -replace "(?s)def club_list\(.*?\):.*?(?=def |\Z)", ""
}
$newClubList = @"

# =====================================================
# CLUBS & VENUES (with weather, maps, events)
# =====================================================

def club_list(request):
    from .models import Club, Event
    from django.utils import timezone
    from django.db.models import Q

    clubs = Club.objects.all().order_by('name')

    county_filter = request.GET.get('county')
    if county_filter:
        clubs = clubs.filter(county=county_filter)

    counties = Club.objects.values_list('county', flat=True).distinct().order_by('county')

    # Group by county, then by category
    county_groups = {}
    now = timezone.now()

    for club in clubs:
        county = club.county or 'Unknown'
        if county not in county_groups:
            county_groups[county] = {}
        cat = club.category or 'General'
        if cat not in county_groups[county]:
            county_groups[county][cat] = []

        upcoming = Event.objects.filter(
            venue__icontains=club.name,
            date__gte=now
        ).order_by('date')[:5]

        event_count = Event.objects.filter(
            venue__icontains=club.name,
            date__gte=now
        ).count()

        weather = None
        if club.lat and club.lon:
            weather = get_weather(club.lat, club.lon)

        county_groups[county][cat].append({
            'club': club,
            'events': upcoming,
            'event_count': event_count,
            'weather': weather,
        })

    context = {
        'county_groups': county_groups,
        'counties': counties,
        'selected_county': county_filter,
        'total_clubs': clubs.count(),
    }
    return render(request, 'events/clubs.html', context)
"@
Add-Content -Path $viewsPath -Value "`n`n$newClubList" -Encoding UTF8
Write-Host "✅ club_list updated with county grouping." -ForegroundColor Green

# 3. Update clubs.html template
$templateDir = "events\templates\events"
New-Item -ItemType Directory -Path $templateDir -Force | Out-Null
$clubsHtml = @"
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <title>Clubs · Black Label</title>
    <link rel="stylesheet" href="{% static 'css/black_label.css' %}">
    <style>
        .club-card{background:#1e1e1e;border-radius:20px;padding:1.2rem;margin-bottom:1rem;border:1px solid #333;}
        .club-header{display:flex;justify-content:space-between;flex-wrap:wrap;}
        .club-meta span{background:#2a2a2a;padding:0.2rem 0.8rem;border-radius:30px;}
        .club-weather{display:flex;align-items:center;gap:0.5rem;color:#ccc;}
        .club-events ul{list-style:none;padding:0;}
        .club-events li{font-size:0.85rem;padding:0.15rem 0;}
        .club-events a{color:#ffd700;text-decoration:none;}
        .county-title{font-size:1.8rem;color:#ffd700;margin-top:2rem;border-bottom:2px solid #333;padding-bottom:0.5rem;}
        .category-title{font-size:1.3rem;color:#aaa;margin-top:1.5rem;border-left:3px solid #ffd700;padding-left:0.8rem;}
    </style>
</head>
<body>
<div class="bl-shell">
    <aside class="bl-sidebar">{% include "events/sidebar.html" %}</aside>
    <main class="bl-main">
        <div class="bl-page-header">
            <div>
                <h1 class="bl-page-title">🏆 Clubs & Venues</h1>
                <p class="bl-page-subtitle">{{ total_clubs }} venues across Kenya</p>
            </div>
        </div>
        <div class="filters">
            <form method="get" class="bl-filter-row">
                <select class="bl-select" name="county">
                    <option value="">All counties</option>
                    {% for county in counties %}
                        <option value="{{ county }}" {% if selected_county == county %}selected{% endif %}>
                            {{ county }}
                        </option>
                    {% endfor %}
                </select>
                <button type="submit" class="bl-btn bl-btn-sm bl-btn-primary">Filter</button>
                <a href="/clubs/" class="bl-btn bl-btn-sm">Clear</a>
            </form>
        </div>
        {% for county, categories in county_groups.items %}
        <h2 class="county-title">📍 {{ county }}</h2>
            {% for category, clubs in categories.items %}
            <h3 class="category-title">{{ category }} <span style="color:#666;font-size:0.9rem;">({{ clubs|length }})</span></h3>
            <div class="bl-grid">
                {% for item in clubs %}
                <div class="club-card">
                    <div class="club-header">
                        <div>
                            <span style="font-weight:600;font-size:1.1rem;">{{ item.club.name }}</span>
                            <span class="bl-badge">{{ item.club.category|default:"General" }}</span>
                        </div>
                        <div class="club-meta">
                            <span>📅 {{ item.event_count }} upcoming</span>
                        </div>
                    </div>
                    <div class="club-weather">
                        {% if item.weather %}
                            <img src="http://openweathermap.org/img/wn/{{ item.weather.icon }}@2x.png" width="36">
                            <span>{{ item.weather.temp }}°C</span>
                            <span>{{ item.weather.condition }}</span>
                            {% if item.weather.rain > 0 %}<span>☔ {{ item.weather.rain }}mm</span>{% endif %}
                        {% else %}
                            <span style="color:#666;">🌤️ No weather data</span>
                        {% endif %}
                    </div>
                    {% if item.events %}
                    <div class="club-events">
                        <p style="color:#888;font-size:0.8rem;">Next events:</p>
                        <ul>
                            {% for event in item.events %}
                            <li>
                                <a href="/events/{{ event.id }}/">{{ event.title|truncatechars:35 }}</a>
                                <span style="color:#666;font-size:0.8rem;">{{ event.date|date:"M j, H:i" }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                    <div style="margin-top:0.5rem;">
                        {% if item.club.lat and item.club.lon %}
                            <a href="https://www.google.com/maps?q={{ item.club.lat }},{{ item.club.lon }}" target="_blank" class="bl-btn bl-btn-sm">🗺️ Map</a>
                        {% endif %}
                        <a href="/events/?venue={{ item.club.name|urlencode }}" class="bl-btn bl-btn-sm">View all events →</a>
                    </div>
                </div>
                {% empty %}
                <p>No clubs in this category.</p>
                {% endfor %}
            </div>
            {% endfor %}
        {% empty %}
        <p>No clubs found. <a href="/scan/">Run a scan</a> to discover venues.</p>
        {% endfor %}
    </main>
</div>
</body>
</html>
"@
$clubsHtml | Out-File -FilePath "$templateDir\clubs.html" -Encoding UTF8
Write-Host "✅ clubs.html updated with county grouping." -ForegroundColor Green

# 4. Create scraper placeholder
$scraperDir = "events\scrapers"
New-Item -ItemType Directory -Path $scraperDir -Force | Out-Null
$eventbriteScraper = @"
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
"@
$eventbriteScraper | Out-File -FilePath "$scraperDir\eventbrite.py" -Encoding UTF8
Write-Host "✅ Eventbrite scraper placeholder created." -ForegroundColor Green

# 5. Management command
$managementDir = "events\management\commands"
New-Item -ItemType Directory -Path $managementDir -Force | Out-Null
New-Item -ItemType File -Path "events\management\__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "events\management\commands\__init__.py" -Force | Out-Null
$scrapeCommand = @"
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
"@
$scrapeCommand | Out-File -FilePath "$managementDir\scrape_all.py" -Encoding UTF8
Write-Host "✅ Scraper management command created." -ForegroundColor Green

Write-Host "`n✅ All updates applied!" -ForegroundColor Green
Write-Host "`n📌 Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your Django server: python manage.py runserver"
Write-Host "2. Visit /clubs/ – see clubs grouped by county with upcoming events."
Write-Host "3. To scrape real events from Eventbrite, get an API key and update events/scrapers/eventbrite.py"
Write-Host "4. Run the scraper: python manage.py scrape_all"
Write-Host "5. For deployment, follow the production checklist."
