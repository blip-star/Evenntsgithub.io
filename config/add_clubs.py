# add_clubs.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import models, connection
from django.utils import timezone
from events.models import Event

# Step 1: Create the Club model (if not exists)
from django.apps import apps
if not apps.is_installed('events.club'):
    # We'll create it dynamically – but easier: just check if table exists
    with connection.cursor() as c:
        try:
            c.execute("SELECT 1 FROM events_club LIMIT 1")
            print("Club table already exists.")
        except:
            print("Club table does not exist. Creating migration...")
            os.system("python manage.py makemigrations events --name add_club_model")
            os.system("python manage.py migrate")

# Step 2: Populate clubs from distinct venues in Event
print("\n📋 Extracting distinct venues from events...")
venues = Event.objects.values_list('venue', 'county').distinct()

clubs_data = {}
for venue, county in venues:
    if not venue:
        continue
    # Clean up venue name (remove common suffixes)
    name = venue.strip()
    # Use the first 200 chars as description placeholder
    desc = f"Popular venue in {county or 'Kenya'} hosting various events."
    clubs_data[name] = {
        'name': name,
        'county': county or 'Nairobi',
        'description': desc,
        'category': 'General'
    }

# Add some known missing venues manually
known_clubs = [
    {'name': 'The Alchemist', 'county': 'Nairobi', 'description': 'Iconic live music and nightlife venue in Westlands.', 'category': 'Nightlife'},
    {'name': 'KICC', 'county': 'Nairobi', 'description': 'Kenya International Convention Centre – major conferences and events.', 'category': 'Conference'},
    {'name': 'Uhuru Gardens', 'county': 'Nairobi', 'description': 'Large public park hosting festivals and outdoor concerts.', 'category': 'Outdoor'},
    {'name': 'Kasarani Stadium', 'county': 'Nairobi', 'description': 'National stadium for sports and large concerts.', 'category': 'Sports'},
    {'name': 'Nyayo Stadium', 'county': 'Nairobi', 'description': 'Multi-purpose stadium for football and events.', 'category': 'Sports'},
    {'name': 'Safaricom Stadium', 'county': 'Nairobi', 'description': 'Modern stadium for sports and entertainment.', 'category': 'Sports'},
    {'name': 'Moi Stadium', 'county': 'Nairobi', 'description': 'Indoor arena for sports and concerts.', 'category': 'Sports'},
    {'name': 'Charter Hall', 'county': 'Nairobi', 'description': 'Popular venue for corporate events and exhibitions.', 'category': 'Corporate'},
    {'name': 'Champions Hall', 'county': 'Nairobi', 'description': 'Indoor arena for boxing and MMA events.', 'category': 'Sports'},
    {'name': 'Nairobi Gymkhana', 'county': 'Nairobi', 'description': 'Sports and social club with event spaces.', 'category': 'Sports'},
    {'name': 'RFUEA Grounds', 'county': 'Nairobi', 'description': 'Rugby and events venue.', 'category': 'Sports'},
    {'name': 'Village Market', 'county': 'Nairobi', 'description': 'Shopping mall with event spaces and food festivals.', 'category': 'Shopping'},
    {'name': 'The Junction', 'county': 'Nairobi', 'description': 'Shopping mall with community events.', 'category': 'Shopping'},
    {'name': 'Two Rivers', 'county': 'Nairobi', 'description': 'Modern mall hosting exhibitions and shows.', 'category': 'Shopping'},
    {'name': 'Westgate Mall', 'county': 'Nairobi', 'description': 'Upscale mall with event spaces.', 'category': 'Shopping'},
    {'name': 'Mamba Village', 'county': 'Nairobi', 'description': 'Venue for live music and cultural events.', 'category': 'Culture'},
    {'name': 'B Club', 'county': 'Nairobi', 'description': 'Nightclub and live music venue.', 'category': 'Nightlife'},
    {'name': 'K1 Club', 'county': 'Nairobi', 'description': 'Popular nightlife destination.', 'category': 'Nightlife'},
    {'name': 'J\'s Bar', 'county': 'Nairobi', 'description': 'Relaxed bar with live music.', 'category': 'Nightlife'},
    {'name': 'J\'s Fresh Bar', 'county': 'Nairobi', 'description': 'Fresh vibe bar and music spot.', 'category': 'Nightlife'},
    {'name': 'Mist Lounge', 'county': 'Nairobi', 'description': 'Classy lounge with DJs and events.', 'category': 'Nightlife'},
    {'name': 'The Blue Door', 'county': 'Nairobi', 'description': 'Intimate live music venue.', 'category': 'Music'},
    {'name': 'Tatu City', 'county': 'Kiambu', 'description': 'Mixed-use development hosting events and races.', 'category': 'Outdoor'},
    {'name': 'Nakuru Athletic Club', 'county': 'Nakuru', 'description': 'Sports and social club in Nakuru.', 'category': 'Sports'},
    {'name': 'Kakamega Showground', 'county': 'Kakamega', 'description': 'Outdoor venue for agricultural shows and events.', 'category': 'Outdoor'},
    {'name': 'Mombasa Sports Club', 'county': 'Mombasa', 'description': 'Sports and social club by the coast.', 'category': 'Sports'},
    {'name': 'Kisumu Showground', 'county': 'Kisumu', 'description': 'Exhibition grounds for events in Kisumu.', 'category': 'Outdoor'},
]

for club in known_clubs:
    clubs_data[club['name']] = club

# Step 3: Insert into Club table
from events.models import Club

created = 0
updated = 0
for name, data in clubs_data.items():
    obj, created_flag = Club.objects.get_or_create(
        name=name,
        defaults={
            'county': data.get('county', 'Nairobi'),
            'description': data.get('description', ''),
            'category': data.get('category', 'General'),
            'image_url': data.get('image_url', ''),
            'website': data.get('website', ''),
        }
    )
    if created_flag:
        created += 1
    else:
        updated += 1

print(f"\n✅ Added {created} new clubs, updated {updated} existing.")

print("\n🎉 Clubs populated successfully!")