from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')

app = Celery('gym')
app.conf.enable_utc = False
app.conf.update(timezone = 'Africa/Maputo')
app.config_from_object(settings, namespace='CELERY')

# Celery Beat Settings
app.conf.beat_schedule = {
    'check-membership-status-every-day': {
        'task': 'membership.tasks.send_subscription_expire_func',
        'schedule': crontab(hour=6, minute=00), 
    },
    'send-subscription-warning-and-send-emails': {
        'task': 'membership.tasks.send_subscription_warning_func',
        'schedule': crontab(hour=6, minute=00), 
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')