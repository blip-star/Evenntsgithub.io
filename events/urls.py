from django.urls import path
from events import views

urlpatterns = [
    # Dashboard & core pages
    path("", views.dashboard, name="dashboard"),
    path("events/", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("social/", views.social_feed, name="social_feed"),
    path("scan/", views.scan_view, name="scan"),
    path("history/", views.scan_history, name="scan_history"),
    path("settings/", views.settings_view, name="settings"),

    # User preferences
    path("preferences/", views.preferences, name="preferences"),

    # Exports
    path("export/events.csv", views.export_events, name="export_events"),
    path("export/events.ics", views.ical_export, name="ical_export"),
    path("events/ical/", views.ical_export, name="ical_subscribe"),

    # Clubs & Venues
    path("clubs/", views.club_list, name="club_list"),
]