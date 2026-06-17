from django.db import models
from django.utils import timezone

class Event(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=500)
    date = models.DateTimeField()
    venue = models.CharField(max_length=500)
    source = models.CharField(max_length=100)
    ticket_url = models.URLField(blank=True)
    county = models.CharField(max_length=100, blank=True)
    price_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_label = models.CharField(max_length=200, blank=True)
    currency = models.CharField(max_length=10, default='KES')
    is_free = models.BooleanField(default=False)
    location_area = models.CharField(max_length=200, blank=True)
    map_lat = models.FloatField(null=True, blank=True)
    map_lon = models.FloatField(null=True, blank=True)
    weather_forecast = models.TextField(blank=True)
    weather_temp_c = models.FloatField(null=True, blank=True)
    weather_rain_pct = models.IntegerField(null=True, blank=True)
    weather_suitable = models.BooleanField(default=False)
    ai_score = models.FloatField(null=True, blank=True)
    ai_category = models.CharField(max_length=100, blank=True)
    ai_reason = models.TextField(blank=True)
    description = models.TextField(blank=True)
    organizer = models.CharField(max_length=300, blank=True)
    is_recommended = models.BooleanField(default=False)
    poster_image_url = models.URLField(blank=True)
    artists = models.JSONField(default=list, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    content_hash = models.CharField(max_length=64, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=500, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['county']),
            models.Index(fields=['ai_score']),
        ]

    def __str__(self):
        return self.title

    @classmethod
    def make_event_id(cls, title, date_iso, venue):
        import hashlib
        raw = f"{title}|{date_iso}|{venue}".lower()
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

class ScanRun(models.Model):
    county = models.CharField(max_length=100)
    days_ahead = models.IntegerField()
    scan_type = models.CharField(max_length=50, default='core')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    events_found = models.IntegerField(default=0)
    events_new = models.IntegerField(default=0)
    events_recommended = models.IntegerField(default=0)
    social_posts_found = models.IntegerField(default=0)
    ai_summary = models.TextField(blank=True)
    weather_summary = models.TextField(blank=True)
    error = models.TextField(blank=True)

class AlertLog(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='alerts')
    channel = models.CharField(max_length=50)
    success = models.BooleanField(default=False)
    content_hash = models.CharField(max_length=64, blank=True)
    alert_type = models.CharField(max_length=20, default='new')
    sent_at = models.DateTimeField(auto_now_add=True)

class SocialPost(models.Model):
    post_url = models.URLField(unique=True)
    platform = models.CharField(max_length=50)
    author = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='social_posts')
    scraped_at = models.DateTimeField(auto_now_add=True)

class AutoScanConfig(models.Model):
    enabled = models.BooleanField(default=True)
    county = models.CharField(max_length=100, default='Nairobi')
    days_ahead = models.IntegerField(default=30)
    interval_hours = models.IntegerField(default=6)
    include_social = models.BooleanField(default=True)

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

class UserPreference(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    preferred_categories = models.TextField(blank=True)
    preferred_counties = models.TextField(blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    free_events_only = models.BooleanField(default=False)
    outdoor_events_only = models.BooleanField(default=False)
    alert_via_telegram = models.BooleanField(default=True)
    alert_via_ntfy = models.BooleanField(default=True)
    alert_via_whatsapp = models.BooleanField(default=True)
    alert_on_price_change = models.BooleanField(default=True)
    alert_on_weather_risk = models.BooleanField(default=True)
    daily_digest = models.BooleanField(default=False)
    digest_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_or_create_for_user(cls, user):
        obj, _ = cls.objects.get_or_create(user=user)
        return obj

class Club(models.Model):
    name = models.CharField(max_length=200, unique=True)
    country = models.CharField(max_length=100, blank=True, default='Kenya')
    county = models.CharField(max_length=100, blank=True)
    location_area = models.CharField(
        max_length=200,
        blank=True,
        help_text='Neighbourhood or street-level location',
    )
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True, default='General')
    image_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def has_coordinates(self):
        return self.lat is not None and self.lon is not None

    @property
    def full_location(self):
        parts = []
        if self.location_area:
            parts.append(self.location_area)
        if self.county and self.county not in parts:
            parts.append(self.county)
        country = self.country or 'Kenya'
        if country not in parts:
            parts.append(country)
        return ', '.join(parts) if parts else country

    class Meta:
        ordering = ['country', 'county', 'name']
