# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-04-04 05:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0017_auto_20180403_1125'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membershiplevel',
            old_name='image',
            new_name='badge',
        ),
    ]
