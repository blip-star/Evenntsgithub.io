from django.contrib import admin
from .models import Event, ScanRun, AlertLog, SocialPost, AutoScanConfig, UserPreference

admin.site.register(Event)
admin.site.register(ScanRun)
admin.site.register(AlertLog)
admin.site.register(SocialPost)
admin.site.register(AutoScanConfig)
admin.site.register(UserPreference)
