# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-01 09:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_ern_burn', '0009_auto_20180301_0909'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statuslevel',
            name='created_user',
        ),
        migrations.RemoveField(
            model_name='statuslevel',
            name='modified_user',
        ),
        migrations.DeleteModel(
            name='StatusLevel',
        ),
    ]