web: gunicorn config.wsgi:application --log-file -
worker: celery worker --app=config.celery:app --loglevel=INFO -B


