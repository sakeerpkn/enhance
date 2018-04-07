# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-15 08:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_baggage', '0015_location_alias'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerbag',
            name='customer_requested_place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='customer_drop_request_place', to='api_baggage.Location'),
        ),
    ]
