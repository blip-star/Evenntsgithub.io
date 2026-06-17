from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import TemplateView

# Optional: simple placeholder view for /clubs/
def clubs_placeholder(request):
    return HttpResponse("<h1>Clubs</h1><p>Coming soon. <a href='/events/'>Back to events</a></p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),          # all events URLs are under root

    # Add clubs/ path – remove this if you don't need it
    path('clubs/', clubs_placeholder, name='clubs'),
]