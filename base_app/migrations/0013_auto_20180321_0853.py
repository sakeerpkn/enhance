# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-21 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0012_pushmessage_dev_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseaddress',
            name='addressline1',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Addressline 1'),
        ),
        migrations.AlterField(
            model_name='baseaddress',
            name='zipcode',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
