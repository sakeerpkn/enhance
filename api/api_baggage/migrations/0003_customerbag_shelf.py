# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-01 11:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_baggage', '0002_auto_20180124_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerbag',
            name='shelf',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]