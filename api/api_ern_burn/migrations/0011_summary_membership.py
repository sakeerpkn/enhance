# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-01 10:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0009_auto_20180301_1044'),
        ('api_ern_burn', '0010_auto_20180301_0917'),
    ]

    operations = [
        migrations.AddField(
            model_name='summary',
            name='membership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base_app.StatusLevel'),
        ),
    ]
