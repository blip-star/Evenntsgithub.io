import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.models import Event, Club
from django.db import connection
from django.utils import timezone

# Step 1: Populate clubs from distinct venues in Event
print("📋 Extracting distinct venues from events...")
venues = Event.objects.values_list('venue', 'county').distinct()

clubs_data = {}
for venue, county in venues:
    if not venue:
        continue
    name = venue.strip()
    desc = f"Popular venue in {county or 'Kenya'} hosting various events."
    clubs_data[name] = {
        'name': name,
        'county': county or 'Nairobi',
        'description': desc,
        'category': 'General',
        'image_url': '',
        'website': ''
    }

# Add known clubs manually (overwrites if present)
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
    {'name': "J's Bar", 'county': 'Nairobi', 'description': 'Relaxed bar with live music.', 'category': 'Nightlife'},
    {'name': "J's Fresh Bar", 'county': 'Nairobi', 'description': 'Fresh vibe bar and music spot.', 'category': 'Nightlife'},
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

# Step 2: Insert/Update clubs
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
        # Update if needed
        if (obj.county != data.get('county', 'Nairobi') or
            obj.description != data.get('description', '') or
            obj.category != data.get('category', 'General')):
            obj.county = data.get('county', 'Nairobi')
            obj.description = data.get('description', '')
            obj.category = data.get('category', 'General')
            obj.image_url = data.get('image_url', '')
            obj.website = data.get('website', '')
            obj.save()
            updated += 1

print(f"\n✅ Added {created} new clubs, updated {updated} existing.")
print("🎉 Clubs populated successfully!")
