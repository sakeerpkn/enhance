# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-01 08:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0002_auto_20180228_0635'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
