# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-09 06:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_baggage', '0011_remove_bag_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
