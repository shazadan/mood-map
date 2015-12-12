from __future__ import division
from __future__ import absolute_import
from collections import Iterable
import re

from django.conf import settings
from django.db import connection
from django.utils import timezone

from twython import TwythonStreamer
from textblob import TextBlob
from datetime import datetime, timedelta
from email.utils import parsedate_tz
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task

import shapefile

from tweets.models import Tweet


# Twitter OAUTH Credentials
APP_KEY = settings.TWITTER_APP_KEY
APP_SECRET = settings.TWITTER_APP_SECRET
OAUTH_TOKEN = settings.TWITTER_OAUTH_TOKEN
OAUTH_TOKEN_SECRET = settings.TWITTER_OAUTH_TOKEN_SECRET

# Long/Lat co-ordinates for twitter:
# (1) southwest pair  (2) northeast pair
geo_coordinates = {'AZ': '-114.818359375,31.3321762085,'
                         '-109.0451965332,37.0042610168',
                    }

# Determine US county name based on long/lat co-ordinates
def geocoord_to_countyname(lat, lon):
    sf = shapefile.Reader("static/shapefiles/county.shp")
    for county in sf.shapeRecords():
        if point_in_polygon(lat, lon, county.shape.points):
            sf = None
            county_name = county.record[5]
            return county_name

# Algorithm to find a point within a polygon
# http://geospatialpython.com/2011/01/point-in-polygon.html
def point_in_polygon(x, y, poly):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

# Make the tweet machine reader friendly
def scrub_tweet(t):
    # Convert to lower case
    t = t.lower()
    # Convert www.* or https?://* to URL
    t = re.sub('((www\.[\s]+)|(https?://[^\s]+))', 'URL', t)
    # Convert @username to AT_USER
    t = re.sub('@[^\s]+', 'AT_USER', t)
    # Remove additional white spaces
    t = re.sub('[\s]+', ' ', t)
    # Replace #word with word
    t = re.sub(r'#([^\s]+)', r'\1', t)
    # trim
    t = t.strip('\'"')
    return t

# Save tweet information to database
@shared_task
def add_tweet(id, created_dt, coordinates, text, county, sentiment_index):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO tweets_tweet (id, created_dt, coordinates, " \
                "text, county, sentiment_index) VALUES (%s, %s, %s, %s, %s, %s);"
        data = (id, created_dt, coordinates, text, county, sentiment_index)
        cursor.execute(query, data)
        connection.commit()
        print 'Tweet saved to DB'
        cursor.close()

    except Exception as e:
        print "Encountered error: (%s)" % e.message

@periodic_task(run_every=(crontab(minute=0, hour="*/3", day_of_week="*")), ignore_result=True)
def delete_tweets():
    # Delete all tweets older than 2 days
    date_from_utc = timezone.now() - timedelta(days=1)
    Tweet.objects.filter(created_dt__lt=date_from_utc).delete()
    print "Deleted tweets older than %s" % str(date_from_utc)

def to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return (dt - timedelta(seconds=time_tuple[-1]))



class MyStreamer(TwythonStreamer):

    def on_success(self, data):

        if 'coordinates' in data:
            county = None
            if isinstance(data['coordinates'], Iterable):
                if 'coordinates' in data['coordinates']:
                    lat = data['coordinates']['coordinates'][0]
                    lon = data['coordinates']['coordinates'][1]
                    county = geocoord_to_countyname(lat, lon)

        if ('text' in data) and (county != None):
            text = scrub_tweet(data['text'])
            analysis = TextBlob(text)
            sentiment_index = analysis.sentiment.polarity

            #print "tweet from %s " % (county.encode('utf-8'))
            print "Tweet arrived at %s" % str(datetime.now())
            add_tweet.delay(id=data['id'],
                      created_dt=str(to_datetime(data['created_at'])),
                      #created_dt='2015-01-01',
                      coordinates=data['coordinates']['coordinates'],
                      text=text.encode('utf-8'),
                      county=county.encode('utf-8'),
                      sentiment_index=sentiment_index)

    def on_error(self, status_code, data):
        print status_code
        print data

    # Want to stop trying to get data because of the error?
    # Uncomment the next line!
    # self.disconnect()

@shared_task
def stream():
    stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    while True:
        try:
            stream.statuses.filter(locations=geo_coordinates['AZ'])
        except:
            continue


