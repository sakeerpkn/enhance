# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-01 09:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_ern_burn', '0008_auto_20180228_0450'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statuslevel',
            old_name='level',
            new_name='id',
        ),
    ]
