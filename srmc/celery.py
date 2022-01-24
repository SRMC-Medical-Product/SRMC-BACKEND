
from __future__ import absolute_import,unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE','srmc.settings')

app=Celery('srmc')
app.conf.enable_utl=False

app.conf.update(timezone="Asia/Kolkata")
app.config_from_object(settings,namespace='CELERY')

app.conf.beat_schedule={
    'send-mail-every-day-at-8':{
        'task':'mainapp.tasks.test_func',
        'schedule':crontab(hour=8,minute=15),
        
    }
}
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
