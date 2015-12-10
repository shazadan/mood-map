#!/bin/bash -e

BASEDIR='/server'

source $BASEDIR/.virtualenvs/01/bin/activate;cd $BASEDIR/projects/mood-map;
python manage.py stream --settings=config.settings.production;
