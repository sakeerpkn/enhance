# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-04-05 12:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_user', '0014_merge_20180405_0750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdetail',
            name='gender',
            field=models.CharField(blank=True, choices=[('female', 'female'), ('male', 'male')], max_length=6, null=True),
        ),
    ]
