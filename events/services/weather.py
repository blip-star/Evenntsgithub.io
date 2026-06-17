import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_current_weather(lat, lon):
    """Fetch current weather from OpenWeatherMap, cached for 30 minutes."""
    if lat is None or lon is None:
        return None

    cache_key = f'weather_{lat:.4f}_{lon:.4f}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
    if not api_key:
        return None

    url = (
        'https://api.openweathermap.org/data/2.5/weather'
        f'?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    )
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            logger.warning('Weather API returned %s for %s,%s', resp.status_code, lat, lon)
            return None

        data = resp.json()
        icon = data['weather'][0]['icon']
        rain = data.get('rain', {})
        weather = {
            'temp': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'humidity': data['main']['humidity'],
            'condition': data['weather'][0]['description'].title(),
            'icon': icon,
            'icon_url': f'https://openweathermap.org/img/wn/{icon}@2x.png',
            'rain': rain.get('1h', 0) or rain.get('3h', 0),
            'wind_speed': round(data.get('wind', {}).get('speed', 0) * 3.6),
        }
        cache.set(cache_key, weather, 60 * 30)
        return weather
    except Exception as exc:
        logger.warning('Weather fetch failed for %s,%s: %s', lat, lon, exc)
    return None


def get_week_summary():
    return (
        'Sat: 24.5°C, 7% rain | Sun: 25.1°C, 4% rain | Mon: 25.0°C, 50% rain | '
        'Tue: 23.5°C, 27% rain | Wed: 23.3°C, 40% rain'
    )
