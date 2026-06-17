# final_setup.ps1
$ErrorActionPreference = "Stop"

Write-Host "🔧 Step 1: Creating Python script..." -ForegroundColor Cyan

$pythonScript = @"
from events.models import AlertLog, Event
from django.db import connection
from django.utils import timezone
import hashlib

# Step 1: Clean orphaned AlertLog records
orphan_ids = [a.id for a in AlertLog.objects.all() if not Event.objects.filter(id=a.event_id).exists()]
if orphan_ids:
    AlertLog.objects.filter(id__in=orphan_ids).delete()
    print(f'Deleted {len(orphan_ids)} orphaned AlertLog records.')
else:
    print('No orphaned AlertLog records found.')

# Step 2: Add unique index on event_id
with connection.cursor() as c:
    try:
        c.execute('DROP INDEX IF EXISTS events_event_event_id_uniq')
    except:
        pass
    c.execute('CREATE UNIQUE INDEX events_event_event_id_uniq ON events_event (event_id);')
    print('Unique index created (or already exists).')

# Step 3: Ensure all sources have at least one event
sources = [
    "Eventbrite","Ticketsasa","Mook","KenyaBuzz","Madfun","Hustlesasa","Luma","Events Plug",
    "HomeBoyz Entertainment","GoodTimes Entertainment","Zuri Events","Events & Conference Organisers Ltd",
    "Expogroup","Aitec Exhibitions & Conferences","Sarit Exhibitions & Promotions",
    "Agricultural Society of Kenya (ASK)","Nairobi Events Guide","Loud Events","Myjiji Events",
    "EventsInNairobi","Gigwapi","254 Entertainment","The Event Factory","Chairmania Events",
    "Ecstatic Africa Events","Blankets & Wine","Africa Nouveau"
]

for source in sources:
    if not Event.objects.filter(source=source).exists():
        raw = f"dummy_for_{source}|2025-01-01|Dummy Venue".lower()
        event_id = hashlib.sha256(raw.encode()).hexdigest()[:32]
        obj, created = Event.objects.get_or_create(
            event_id=event_id,
            defaults={
                'title': f"Dummy event for {source}",
                'venue': 'Dummy Venue',
                'date': timezone.now(),
                'source': source,
                'county': 'Nairobi',
                'ai_score': 0,
                'description': 'Placeholder – remove after real events are added.'
            }
        )
        print(f'✅ Added dummy event for {source}')
    else:
        print(f'⏩ Source {source} already has events.')

print('\n✅ All steps completed successfully.')
"@

# Write the Python script to a file
$pythonScript | Out-File -FilePath "add_sources.py" -Encoding UTF8

Write-Host "🔧 Step 2: Running Python script in Django shell..." -ForegroundColor Cyan
python manage.py shell -c "exec(open('add_sources.py').read())"

Write-Host "`n✅ Done! All sources now appear in the dropdown." -ForegroundColor Green
Write-Host "`n📌 Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your Django server (Ctrl+C then python manage.py runserver)."
Write-Host "2. Visit /events/ – the Source dropdown will show all sources."
Write-Host "3. To remove dummy events later: python manage.py shell -c `"from events.models import Event; Event.objects.filter(title__startswith='Dummy event for').delete()`""
Write-Host "4. You can delete add_sources.py after it runs."