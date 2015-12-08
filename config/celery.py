from __future__ import absolute_import

import os
from celery import Celery
from django.conf import settings

from tweets.tasks import stream

# set the default Django settings module for the 'celery' program.
# TODO: make this dynamic based on environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

print os.environ

app = Celery('mood-map')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

stream.delay()