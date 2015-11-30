from __future__ import division
from collections import Iterable
import re

from django.conf import settings

from twython import TwythonStreamer
import shapefile
from textblob import TextBlob


# Twitter OAUTH Credentials
APP_KEY = settings.TWITTER_APP_KEY
APP_SECRET = settings.TWITTER_APP_SECRET
OAUTH_TOKEN = settings.TWITTER_OAUTH_TOKEN
OAUTH_TOKEN_SECRET = settings.TWITTER_OAUTH_TOKEN_SECRET

# long/lat (1) southwest pair  (2) northeast pair
geo_coordinates = {'AZ': '-114.818359375,31.3321762085,'
                         '-109.0451965332,37.0042610168'}


def geocoord_to_countyname(lat, lon):
    sf = shapefile.Reader("static/shapefiles/county.shp")
    for county in sf.shapeRecords():
        if point_in_polygon(lat, lon, county.shape.points):
            sf = None
            county_name = county.record[5]
            return county_name


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


# Process tweet to make it more machine readable
def process_tweet(t):
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


class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        # if 'text' in data:
        # print data['text'].encode('utf-8')
        if 'coordinates' in data:
            county = None
            if isinstance(data['coordinates'], Iterable):
                if 'coordinates' in data['coordinates']:
                    lat = data['coordinates']['coordinates'][0]
                    lon = data['coordinates']['coordinates'][1]
                    county = geocoord_to_countyname(lat, lon)

        if ('text' in data) and (county != None):
            text = process_tweet(data['text'])
            analysis = TextBlob(text)
            sentiment = analysis.sentiment.polarity

            mood = None
            if sentiment >= -0.05 and sentiment <= 0.05:
                mood = 'Neutral'
            elif sentiment < -0.05:
                mood = 'Negative'
            elif sentiment > 0.05:
                mood = 'Positive'
            else:
                mood = 'Neutral'

            print "Tweet: %s" % text.encode('utf-8')
            print "From: %s" % county
            print "Mood: %s (%.2f)\n" %  (mood, sentiment)


def on_error(self, status_code, data):
    print status_code

    # Want to stop trying to get data because of the error?
    # Uncomment the next line!
    # self.disconnect()


def stream():
    stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    # stream.statuses.filter(track='phoenix')
    stream.statuses.filter(locations=geo_coordinates['AZ'])

