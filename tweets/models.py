from django.db import models

# Create your models here.
class Tweet(models.Model):
    tweet_id = models.CharField(max_length=20)
    created_dt = models.DateTimeField()
    coordinates = models.CharField(max_length=50)
    text = models.CharField(max_length=150)
    county = models.CharField(max_length=50)
    sentiment_index = models.FloatField()