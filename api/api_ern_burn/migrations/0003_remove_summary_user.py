# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-27 08:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_ern_burn', '0002_auto_20180227_0853'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summary',
            name='user',
        ),
    ]
