#!/bin/bash -e

BASEDIR='/server'

source $BASEDIR/.virtualenvs/01/bin/activate;cd $BASEDIR/projects/mood-map;echo "from tweets.tasks import stream; stream()" | python manage.py shell --settings=config.settings.local;
