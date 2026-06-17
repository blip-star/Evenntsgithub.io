from django.db import models
from django.contrib.auth.models import User

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_categories = models.TextField(blank=True, help_text="Comma‑separated")
    preferred_counties = models.TextField(blank=True, help_text="Comma‑separated")
    alert_via_telegram = models.BooleanField(default=True)
    alert_via_whatsapp = models.BooleanField(default=True)
    daily_digest = models.BooleanField(default=False)
    # add more fields as needed

    @classmethod
    def get_or_create_for_user(cls, user):
        obj, _ = cls.objects.get_or_create(user=user)
        return obj