# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-24 13:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_user', '0003_auto_20180124_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userotp',
            name='mobile_number',
            field=models.CharField(max_length=1024),
        ),
    ]
