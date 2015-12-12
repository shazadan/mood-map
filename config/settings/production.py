import dj_database_url
from datetime import timedelta

from .base import *

DEBUG = False

ADMINS = (('Admin', get_env_variable('DEFAULT_FROM_EMAIL')),)
MANAGERS = ADMINS

# EMAIL CONFIGURATION
# ===================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_variable('EMAIL_HOST')
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = get_env_variable('DEFAULT_FROM_EMAIL')

ALLOWED_HOSTS = ['*']

DATABASES = {'default': dj_database_url.config()}

STATIC_ROOT = 'staticfiles'

BROKER_URL = get_env_variable('REDIS_URL')
CELERY_RESULT_BACKEND = get_env_variable('REDIS_URL')
CELERY_REDIS_MAX_CONNECTIONS = 15

CELERYBEAT_SCHEDULE = {
    'delete-every-hour': {
        'task': 'tweets.tasks.delete_tweets',
        'schedule': timedelta(hours=1)
    },
}

CELERY_TIMEZONE = 'UTC'