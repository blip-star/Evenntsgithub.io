from django.contrib.auth.decorators import login_required
from events.forms import UserPreferenceForm
from django.http import HttpResponse
from icalendar import Calendar, Event as ICalEvent
from django.utils import timezone

def ical_export(request):
    cal = Calendar()
    cal.add('prodid', '-//Nairobi Events Bot//')
    cal.add('version', '2.0')
    upcoming = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:200]
    for ev in upcoming:
        ical = ICalEvent()
        ical.add('summary', ev.title)
        ical.add('dtstart', ev.date)
        ical.add('location', ev.venue)
        ical.add('description', f"Ticket: {ev.url}\nScore: {ev.ai_score}")
        cal.add_component(ical)
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename="events.ics"'
    return response
@login_required
def preferences(request):
    prefs = UserPreference.get_or_create_for_user(request.user)
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferences saved.")
            return redirect('preferences')
    else:
        form = UserPreferenceForm(instance=prefs)
    return render(request, 'events/preferences.html', {'form': form})