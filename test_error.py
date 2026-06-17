import os
import sys
import django

sys.path.insert(0, r'E:\EVENTS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from events.views import event_list

factory = RequestFactory()
request = factory.get('/events/')
request.META['HTTP_HOST'] = 'testserver'

try:
    response = event_list(request)
    print("Status:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
