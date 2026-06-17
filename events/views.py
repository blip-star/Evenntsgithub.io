import csv
import logging
from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from icalendar import Calendar, Event as ICalEvent

from events.models import Event, ScanRun, SocialPost, AutoScanConfig, UserPreference, Club
from events.services.scanner import run_scan
from events.services.weather import get_week_summary, get_current_weather
from events.services.whatsapp import is_whatsapp_ready
from events.services.ntfy_push import ntfy_status

logger = logging.getLogger(__name__)

def dashboard(request):
    now = timezone.now()
    upcoming = Event.objects.filter(date__gte=now).order_by('date')
    recommended_count = upcoming.filter(is_recommended=True).count()
    events = upcoming[:12]
    weather = get_week_summary()
    return render(request, 'events/dashboard.html', {
        'events': events,
        'recommended': recommended_count,
        'weather': weather,
    })


def event_list(request):
    events = Event.objects.all().order_by('-date')
    sources = Event.objects.values_list('source', flat=True).distinct().order_by('source')
    counties = Event.objects.values_list('county', flat=True).distinct().order_by('county')

    source_filter = request.GET.get('source')
    if source_filter:
        events = events.filter(source=source_filter)

    county_filter = request.GET.get('county')
    if county_filter:
        events = events.filter(county=county_filter)

    category_filter = request.GET.get('category')
    if category_filter:
        events = events.filter(ai_category=category_filter)

    venue_filter = request.GET.get('venue')
    if venue_filter:
        events = events.filter(venue__icontains=venue_filter)

    context = {
        'events': events,
        'sources': sources,
        'counties': counties,
        'selected_source': source_filter,
        'selected_county': county_filter,
        'selected_category': request.GET.get('category', ''),
        'selected_venue': venue_filter,
        'event_count': events.count(),
    }
    return render(request, 'events/list.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})


def social_feed(request):
    posts = SocialPost.objects.select_related('event').order_by('-scraped_at')[:20]
    return render(request, 'events/social_feed.html', {'posts': posts})


@csrf_protect
def scan_view(request):
    config = AutoScanConfig.get_config()
    if request.method == 'POST':
        action = request.POST.get('action', 'scan')
        if action == 'autoscan':
            config.enabled = request.POST.get('enabled') == 'on'
            config.county = request.POST.get('county', config.county)
            config.days_ahead = int(request.POST.get('days_ahead', config.days_ahead))
            config.interval_hours = int(request.POST.get('interval_hours', config.interval_hours))
            config.include_social = request.POST.get('include_social') == 'on'
            config.save()
            messages.success(request, f"Autoscan {'enabled' if config.enabled else 'disabled'}.")
            return redirect('scan')
        else:
            county = request.POST.get('county', settings.EVENTS_DEFAULT_COUNTY)
            days_ahead = int(request.POST.get('days_ahead', settings.EVENTS_DEFAULT_DAYS_AHEAD))
            dry_run = request.POST.get('dry_run') == 'on'
            include_social = request.POST.get('include_social') == 'on'
            try:
                scan = run_scan(county, days_ahead, alert_new_only=True, dry_run=dry_run, include_social=include_social)
                if scan.error:
                    messages.error(request, f"Scan failed: {scan.error}")
                else:
                    messages.success(request, f"Scan complete: {scan.events_found} found, {scan.events_new} new.")
            except Exception as e:
                messages.error(request, f"Scan error: {e}")
            return redirect('scan')
    recent_scans = ScanRun.objects.all()[:10]
    return render(request, 'events/scan.html', {
        'config': config,
        'recent_scans': recent_scans,
    })


def scan_history(request):
    scans = ScanRun.objects.all().order_by('-started_at')[:50]
    return render(request, 'events/scan_history.html', {'scans': scans})


def settings_view(request):
    telegram_configured = bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_IDS)
    whatsapp_ready = is_whatsapp_ready()
    ntfy = ntfy_status()
    context = {
        'telegram_configured': telegram_configured,
        'whatsapp_configured': whatsapp_ready,
        'ntfy_configured': ntfy.get('configured', False),
        'llm_provider': getattr(settings, 'LLM_PROVIDER', 'none'),
    }
    return render(request, 'events/settings.html', context)


@login_required
def preferences(request):
    prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        prefs.preferred_categories = request.POST.get('preferred_categories', '')
        prefs.preferred_counties = request.POST.get('preferred_counties', '')
        prefs.min_price = request.POST.get('min_price') or None
        prefs.max_price = request.POST.get('max_price') or None
        prefs.free_events_only = request.POST.get('free_events_only') == 'on'
        prefs.outdoor_events_only = request.POST.get('outdoor_events_only') == 'on'
        prefs.alert_via_telegram = request.POST.get('alert_via_telegram') == 'on'
        prefs.alert_via_ntfy = request.POST.get('alert_via_ntfy') == 'on'
        prefs.alert_via_whatsapp = request.POST.get('alert_via_whatsapp') == 'on'
        prefs.daily_digest = request.POST.get('daily_digest') == 'on'
        prefs.digest_time = request.POST.get('digest_time') or None
        prefs.save()
        messages.success(request, "Preferences saved.")
        return redirect('preferences')
    return render(request, 'events/preferences.html', {'prefs': prefs})


def ical_export(request):
    cal = Calendar()
    cal.add('prodid', '-//Nairobi Events Bot//')
    cal.add('version', '2.0')
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:200]
    for ev in events:
        ical = ICalEvent()
        ical.add('summary', ev.title)
        ical.add('dtstart', ev.date)
        ical.add('location', ev.venue)
        cal.add_component(ical)
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename="events.ics"'
    return response


def export_events(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="events.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Date', 'Venue', 'Source', 'Score'])
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:500]
    for ev in events:
        writer.writerow([ev.title, ev.date.isoformat(), ev.venue, ev.source, ev.ai_score])
    return response


def club_list(request):
    """Venue directory grouped by country → county → category with live weather."""
    now = timezone.now()
    qs = Club.objects.all()

    country_filter = request.GET.get('country', '').strip()
    county_filter = request.GET.get('county', '').strip()
    category_filter = request.GET.get('category', '').strip()

    if country_filter:
        qs = qs.filter(country__iexact=country_filter)
    if county_filter:
        qs = qs.filter(county__iexact=county_filter)
    if category_filter:
        qs = qs.filter(category__iexact=category_filter)

    clubs = qs.order_by('country', 'county', 'category', 'name')
    total_clubs = clubs.count()

    countries = (
        Club.objects.exclude(country='')
        .values_list('country', flat=True)
        .distinct()
        .order_by('country')
    )
    counties = (
        Club.objects.exclude(county='')
        .values_list('county', flat=True)
        .distinct()
        .order_by('county')
    )
    categories = (
        Club.objects.exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )

    country_groups = OrderedDict()
    country_stats = {}
    total_upcoming_events = 0
    weather_available = 0

    for club in clubs:
        country = club.country or 'Kenya'
        county = club.county or 'Unknown'
        category = club.category or 'General'

        if country not in country_groups:
            country_groups[country] = OrderedDict()
            country_stats[country] = {'venues': 0, 'counties': set()}

        if county not in country_groups[country]:
            country_groups[country][county] = OrderedDict()

        if category not in country_groups[country][county]:
            country_groups[country][county][category] = []

        upcoming = (
            Event.objects.filter(venue__icontains=club.name, date__gte=now)
            .order_by('date')[:5]
        )
        event_count = Event.objects.filter(
            venue__icontains=club.name,
            date__gte=now,
        ).count()
        total_upcoming_events += event_count

        weather = get_current_weather(club.lat, club.lon) if club.has_coordinates else None
        if weather:
            weather_available += 1

        country_groups[country][county][category].append({
            'club': club,
            'events': upcoming,
            'event_count': event_count,
            'weather': weather,
        })
        country_stats[country]['venues'] += 1
        country_stats[country]['counties'].add(county)

    for stats in country_stats.values():
        stats['county_count'] = len(stats['counties'])
        del stats['counties']

    country_sections = []
    for country, counties_map in country_groups.items():
        country_sections.append({
            'country': country,
            'county_groups': counties_map,
            'venue_count': country_stats[country]['venues'],
            'region_count': country_stats[country]['county_count'],
        })

    return render(request, 'events/clubs.html', {
        'country_sections': country_sections,
        'countries': countries,
        'counties': counties,
        'categories': categories,
        'selected_country': country_filter,
        'selected_county': county_filter,
        'selected_category': category_filter,
        'total_clubs': total_clubs,
        'country_count': len(country_groups),
        'county_count': len(counties),
        'total_upcoming_events': total_upcoming_events,
        'weather_available': weather_available,
        'weather_configured': bool(getattr(settings, 'OPENWEATHER_API_KEY', None)),
    })
