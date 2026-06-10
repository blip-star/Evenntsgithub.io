from django.shortcuts import render
from django.http import HttpResponse
from events.models import Event
from django.utils import timezone

def dashboard(request):
    upcoming = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:10]
    return render(request, 'events/dashboard.html', {'events': upcoming})

def event_list(request):
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, pk):
    event = Event.objects.get(pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})

def scan_view(request):
    return HttpResponse("Scan view - use management command")

def social_feed(request):
    return HttpResponse("Social feed placeholder")

def preferences(request):
    return HttpResponse("Preferences placeholder")

def ical_export(request):
    return HttpResponse("iCal export placeholder")

def settings_view(request):
    return HttpResponse("Settings placeholder")

def scan_history(request):
    return HttpResponse("Scan history placeholder")
