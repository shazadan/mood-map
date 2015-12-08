web: gunicorn config.wsgi:application --log-file -
worker: python celery worker --app=config.celery:app --loglevel=INFO


