from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Desk2.settings')

app = Celery('desk2')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
