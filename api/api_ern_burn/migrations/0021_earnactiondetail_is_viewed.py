# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-26 11:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_ern_burn', '0020_auto_20180326_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='earnactiondetail',
            name='is_viewed',
            field=models.BooleanField(default=False),
        ),
    ]
