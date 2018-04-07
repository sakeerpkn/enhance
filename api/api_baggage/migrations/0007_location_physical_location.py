# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-20 04:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_baggage', '0006_physicallocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='physical_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='zones', to='api_baggage.PhysicalLocation'),
        ),
    ]
