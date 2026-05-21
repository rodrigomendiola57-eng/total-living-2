import os
import django

os.chdir('C:\\TOTAL LIVING')
os.environ['DJANGO_SETTINGS_MODULE'] = 'total_living.settings.development'
django.setup()

from total_living.urls import home_view
from django.test import RequestFactory

rf = RequestFactory()
req = rf.get('/')

try:
    resp = home_view(req)
    print('Vista funciona! Status:', resp.status_code)
    print('Content-Type:', resp.get('Content-Type'))
except Exception as e:
    print('ERROR en vista:', type(e).__name__, '-', e)
    import traceback
    traceback.print_exc()
