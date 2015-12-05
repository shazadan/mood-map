from django.shortcuts import render_to_response
from django.http import Http404
from django.db.models import Count, Sum, Case, IntegerField, When, Avg
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json

from tweets.models import Tweet




# Create your views here.
#def index(request):
#    context = {}
#    return render(request, 'index.html', context)

AZ_COUNTIES = ['Apache', 'Cochise', 'Coconino',  'Gila', 'Graham',
               'Greenlee', 'La Paz', 'Maricopa', 'Mohave', 'Navajo', 'Pima',
               'Pinal', 'Santa Cruz', 'Yavapai', 'Yuma']

def index(request):
    context = {}
    try:
        #tweets_by_county = Tweet.objects.filter(
        # county__in=AZ_COUNTIES).values(
        #    'county').annotate(count=Count(
        #    'county')).order_by('-count')

        tweets_by_county = Tweet.objects.filter(
            county__in=AZ_COUNTIES).values('county').annotate(
            count=Count('county')).order_by('-count')

        tweets_stats = Tweet.objects.filter(
            county__in=AZ_COUNTIES).values('county').annotate(
            count=Avg('sentiment_index')).order_by('-count')

        data = json.dumps(list(tweets_stats))

        #data = serializers.serialize("json",  tweets_by_county)

        context = {'tweet_stats': tweets_stats,
                   'data': data}
    except Tweet.DoesNotExist:
        raise Http404("tweet does not exist")

    return render_to_response('index.html', context)