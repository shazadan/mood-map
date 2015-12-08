web: gunicorn config.wsgi:application --log-file -
worker: celery worker --app=config.celery:app --loglevel=INFO
streamer: echo "from tweets.tasks import stream; stream()" | heroku run python manage.py shell


