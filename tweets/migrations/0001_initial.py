# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('created_dt', models.DateField()),
                ('coordinates', models.CharField(max_length=50)),
                ('text', models.CharField(max_length=150)),
                ('county', models.CharField(max_length=50)),
                ('sentiment_index', models.FloatField()),
            ],
        ),
    ]
