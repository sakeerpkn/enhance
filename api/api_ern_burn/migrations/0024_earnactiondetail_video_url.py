# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-28 05:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_ern_burn', '0023_auto_20180327_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='earnactiondetail',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]