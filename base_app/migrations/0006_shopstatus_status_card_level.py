# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-01 09:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0005_statuslevel'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopstatus',
            name='status_card_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='base_app.StatusLevel'),
        ),
    ]
