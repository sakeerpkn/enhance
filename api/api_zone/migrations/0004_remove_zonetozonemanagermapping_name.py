# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-06 09:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_zone', '0003_auto_20180206_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zonetozonemanagermapping',
            name='name',
        ),
    ]
