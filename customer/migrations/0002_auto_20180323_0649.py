# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-23 06:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagesgallery',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
