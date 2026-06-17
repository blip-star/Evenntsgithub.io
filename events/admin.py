from django.contrib import admin
from .models import Event, ScanRun, AlertLog, SocialPost, AutoScanConfig, UserPreference, Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'county', 'location_area', 'category', 'lat', 'lon')
    list_filter = ('country', 'county', 'category')
    search_fields = ('name', 'location_area', 'county', 'country')


admin.site.register(Event)
admin.site.register(ScanRun)
admin.site.register(AlertLog)
admin.site.register(SocialPost)
admin.site.register(AutoScanConfig)
admin.site.register(UserPreference)
