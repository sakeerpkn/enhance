# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-15 06:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_baggage', '0014_customerbag_customer_requested_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='alias',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]