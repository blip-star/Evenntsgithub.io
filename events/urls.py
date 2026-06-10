from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('scan/', views.scan_view, name='scan'),
    path('social/', views.social_feed, name='social_feed'),
    path('preferences/', views.preferences, name='preferences'),
    path('export/events.ics', views.ical_export, name='ical_export'),
    path('settings/', views.settings_view, name='settings'),
    path('history/', views.scan_history, name='scan_history'),
]
