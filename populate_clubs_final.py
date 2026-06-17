"""Populate Club records with country, location, and coordinates."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.models import Club

CLUBS_DATA = [
    {
        'name': 'The Alchemist', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Westlands', 'lat': -1.2682, 'lon': 36.7993,
        'category': 'Nightlife', 'description': 'Iconic live music and nightlife venue in Westlands.',
    },
    {
        'name': 'KICC', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'City Centre, Harambee Avenue', 'lat': -1.2884, 'lon': 36.8233,
        'category': 'Conference', 'description': 'Kenya International Convention Centre – major conferences.',
    },
    {
        'name': 'Uhuru Gardens', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': "Lang'ata Road", 'lat': -1.3083, 'lon': 36.8160,
        'category': 'Outdoor', 'description': 'Large public park hosting festivals and concerts.',
    },
    {
        'name': 'Kasarani Stadium', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Kasarani', 'lat': -1.2287, 'lon': 36.8919,
        'category': 'Stadium', 'description': 'National stadium for sports and large concerts.',
    },
    {
        'name': 'Nyayo Stadium', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Ngong Road', 'lat': -1.2986, 'lon': 36.8269,
        'category': 'Stadium', 'description': 'Multi-purpose stadium for football and events.',
    },
    {
        'name': 'Safaricom Stadium', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Madaraka', 'lat': -1.3256, 'lon': 36.8298,
        'category': 'Stadium', 'description': 'Modern stadium for sports and concerts.',
    },
    {
        'name': 'Moi Stadium', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Ngong Road', 'lat': -1.2934, 'lon': 36.8401,
        'category': 'Stadium', 'description': 'Indoor arena for sports and concerts.',
    },
    {
        'name': 'Charter Hall', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'City Centre', 'lat': -1.2892, 'lon': 36.8214,
        'category': 'Conference', 'description': 'Popular venue for corporate events and exhibitions.',
    },
    {
        'name': 'Champions Hall', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Ngong Road', 'lat': -1.2857, 'lon': 36.8355,
        'category': 'Stadium', 'description': 'Indoor arena for boxing, MMA, and combat sports.',
    },
    {
        'name': 'Nairobi Gymkhana', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Ngong Road', 'lat': -1.2831, 'lon': 36.8180,
        'category': 'Sports', 'description': 'Sports and social club with event spaces.',
    },
    {
        'name': 'RFUEA Grounds', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Ngong Road', 'lat': -1.2899, 'lon': 36.8351,
        'category': 'Sports', 'description': 'Rugby and events venue.',
    },
    {
        'name': 'Village Market', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Gigiri', 'lat': -1.2338, 'lon': 36.8048,
        'category': 'Shopping', 'description': 'Shopping mall with event spaces and food festivals.',
    },
    {
        'name': 'The Junction', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Ngong Road', 'lat': -1.2834, 'lon': 36.7964,
        'category': 'Shopping', 'description': 'Shopping mall with community events.',
    },
    {
        'name': 'Two Rivers', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Ruaka', 'lat': -1.2080, 'lon': 36.7990,
        'category': 'Shopping', 'description': 'Modern mall hosting exhibitions and shows.',
    },
    {
        'name': 'Westgate Mall', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Westlands', 'lat': -1.2637, 'lon': 36.8035,
        'category': 'Shopping', 'description': 'Upscale mall with event spaces.',
    },
    {
        'name': 'Mamba Village', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Langata', 'lat': -1.2794, 'lon': 36.8064,
        'category': 'Culture', 'description': 'Venue for live music and cultural events.',
    },
    {
        'name': 'B Club', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Westlands', 'lat': -1.2693, 'lon': 36.8012,
        'category': 'Nightlife', 'description': 'Nightclub and live music venue.',
    },
    {
        'name': 'K1 Club', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Westlands', 'lat': -1.2644, 'lon': 36.7999,
        'category': 'Nightlife', 'description': 'Popular nightlife destination.',
    },
    {
        'name': "J's Bar", 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Westlands', 'lat': -1.2718, 'lon': 36.7960,
        'category': 'Nightlife', 'description': 'Relaxed bar with live music.',
    },
    {
        'name': "J's Fresh Bar", 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Westlands', 'lat': -1.2743, 'lon': 36.8021,
        'category': 'Nightlife', 'description': 'Fresh vibe bar and music spot.',
    },
    {
        'name': 'Mist Lounge', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Westlands', 'lat': -1.2674, 'lon': 36.7987,
        'category': 'Nightlife', 'description': 'Classy lounge with DJs and hookah.',
    },
    {
        'name': 'The Blue Door', 'country': 'Kenya', 'county': 'Nairobi',
        'location_area': 'Westlands', 'lat': -1.2722, 'lon': 36.8036,
        'category': 'Nightlife', 'description': 'Intimate live music venue and bar.',
    },
    {
        'name': 'Tatu City', 'country': 'Kenya', 'county': 'Kiambu',
        'location_area': 'Tatu City', 'lat': -1.1908, 'lon': 36.8038,
        'category': 'Outdoor', 'description': 'Mixed-use development hosting events and races.',
    },
    {
        'name': 'Ruiru Sports Complex', 'country': 'Kenya', 'county': 'Kiambu',
        'location_area': 'Ruiru', 'lat': -1.1495, 'lon': 36.9597,
        'category': 'Sports', 'description': 'Sports and events complex in Ruiru.',
    },
    {
        'name': 'Nakuru Athletic Club', 'country': 'Kenya', 'county': 'Nakuru',
        'location_area': 'Nakuru Town', 'lat': -0.3031, 'lon': 36.0803,
        'category': 'Sports', 'description': 'Sports and social club in Nakuru.',
    },
    {
        'name': 'Kakamega Showground', 'country': 'Kenya', 'county': 'Kakamega',
        'location_area': 'Kakamega Town', 'lat': 0.2827, 'lon': 34.7519,
        'category': 'Outdoor', 'description': 'Outdoor venue for agricultural shows and events.',
    },
    {
        'name': 'Mombasa Sports Club', 'country': 'Kenya', 'county': 'Mombasa',
        'location_area': 'Mombasa Island', 'lat': -4.0435, 'lon': 39.6682,
        'category': 'Sports', 'description': 'Sports and social club by the coast.',
    },
    {
        'name': 'Kisumu Showground', 'country': 'Kenya', 'county': 'Kisumu',
        'location_area': 'Kisumu City', 'lat': -0.1022, 'lon': 34.7617,
        'category': 'Outdoor', 'description': 'Exhibition grounds for events in Kisumu.',
    },
    {
        'name': 'Kipchoge Keino Stadium', 'country': 'Kenya', 'county': 'Uasin Gishu',
        'location_area': 'Eldoret', 'lat': 0.5143, 'lon': 35.2698,
        'category': 'Stadium', 'description': 'Multi-purpose stadium in Eldoret.',
    },
    {
        'name': "Machakos People's Park", 'country': 'Kenya', 'county': 'Machakos',
        'location_area': 'Machakos Town', 'lat': -1.5177, 'lon': 37.2634,
        'category': 'Outdoor', 'description': 'Public park for outdoor events and concerts.',
    },
]

UPDATE_FIELDS = [
    'country', 'county', 'location_area', 'lat', 'lon', 'category', 'description',
]

if __name__ == '__main__':
    created = updated = 0
    for data in CLUBS_DATA:
        obj, is_new = Club.objects.get_or_create(
            name=data['name'],
            defaults={field: data.get(field, '') for field in UPDATE_FIELDS},
        )
        if is_new:
            created += 1
            continue

        changed = False
        for field in UPDATE_FIELDS:
            new_val = data.get(field, '')
            if getattr(obj, field) != new_val:
                setattr(obj, field, new_val)
                changed = True
        if changed:
            obj.save(update_fields=UPDATE_FIELDS)
            updated += 1

    print(f'Clubs: {created} created, {updated} updated, {Club.objects.count()} total.')
