# add_sources.py
from events.models import AlertLog, Event
from django.db import connection
from django.utils import timezone
import hashlib

# Step 1: Clean orphaned AlertLog records
print("🔧 Cleaning orphaned AlertLog records...")
orphan_ids = [a.id for a in AlertLog.objects.all() if not Event.objects.filter(id=a.event_id).exists()]
if orphan_ids:
    AlertLog.objects.filter(id__in=orphan_ids).delete()
    print(f'✅ Deleted {len(orphan_ids)} orphaned AlertLog records.')
else:
    print('✅ No orphaned AlertLog records found.')

# Step 2: Add unique index on event_id
print("\n🔒 Adding unique index on event_id...")
with connection.cursor() as c:
    try:
        c.execute('DROP INDEX IF EXISTS events_event_event_id_uniq')
    except:
        pass
    c.execute('CREATE UNIQUE INDEX events_event_event_id_uniq ON events_event (event_id);')
    print('✅ Unique index created (or already exists).')

# Step 3: Ensure all sources have at least one event
sources = [
    "Eventbrite", "Ticketsasa", "Mook", "KenyaBuzz", "Madfun", "Hustlesasa", "Luma", "Events Plug",
    "HomeBoyz Entertainment", "GoodTimes Entertainment", "Zuri Events", "Events & Conference Organisers Ltd",
    "Expogroup", "Aitec Exhibitions & Conferences", "Sarit Exhibitions & Promotions",
    "Agricultural Society of Kenya (ASK)", "Nairobi Events Guide", "Loud Events", "Myjiji Events",
    "EventsInNairobi", "Gigwapi", "254 Entertainment", "The Event Factory", "Chairmania Events",
    "Ecstatic Africa Events", "Blankets & Wine", "Africa Nouveau"
]

print("\n📦 Adding dummy events for sources that need them...")
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

print('\n✅ All steps completed successfully!')