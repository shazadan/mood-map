import dj_database_url

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
