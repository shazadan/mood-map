import json
from datetime import datetime, date, timedelta

from django.shortcuts import render_to_response
from django.http import Http404
from django.db.models import Count, Case, DecimalField, When, Avg
from django.utils import timezone
from django.db.models import Q

from tweets.models import Tweet
from core.models import get_query

AZ_COUNTIES = ['Apache', 'Cochise', 'Coconino', 'Gila', 'Graham',
               'Greenlee', 'La Paz', 'Maricopa', 'Mohave', 'Navajo', 'Pima',
               'Pinal', 'Santa Cruz', 'Yavapai', 'Yuma']


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, float):
            return round(obj, 4)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def index(request):
    context = {}
    query_string = ''
    found_entries = None
    entry_query = Q()
    try:
        # get tweets within the last 24 hours and that belong to AZ counties
        #date_from_utc = timezone.now() - timedelta(days=1)

        if ('q' in request.GET) and request.GET['q'].strip():
            query_string = request.GET['q']
            entry_query = get_query(query_string, ['text',])

        mood_by_geo = Tweet.objects.filter(
            county__in=AZ_COUNTIES #, created_dt__gte=date_from_utc,
            ).filter(entry_query).values(
            'county').annotate(
            avg_index=Avg(Case(When(sentiment_index__gt=0, then=1),
                               When(sentiment_index__lt=0, then=-1),
                               default=0.001,
                               output_field=DecimalField())),
            num_tweets=Count('county'))

        mood_by_geo_json = json.dumps(list(mood_by_geo))

        context = {'tweet_stats': mood_by_geo,
                   'mood_by_geo': mood_by_geo_json,
                   'query_string': query_string,}

    except Tweet.DoesNotExist:
        raise Http404("tweet does not exist")

    return render_to_response('index.html', context)

def search(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'body',])

        found_entries = Tweets.objects.filter(entry_query).order_by(
        '-pub_date')

    return render_to_response('search/search_results.html',
                          { 'query_string': query_string, 'found_entries': found_entries },
                          context_instance=RequestContext(request))