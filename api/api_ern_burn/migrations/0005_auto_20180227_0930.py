# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-27 09:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_ern_burn', '0004_summary_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EurnBurnSettings',
            new_name='ErnBurnSettings',
        ),
        migrations.AlterField(
            model_name='summary',
            name='balance_points',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='summary',
            name='erned_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='summary',
            name='total_burn_points',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='summary',
            name='total_ern_points',
            field=models.FloatField(default=0.0),
        ),
    ]