# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-20 04:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_baggage', '0005_auto_20180206_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhysicalLocation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]
