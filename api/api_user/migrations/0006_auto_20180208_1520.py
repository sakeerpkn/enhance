# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-08 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_user', '0005_profiledetails_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiledetails',
            name='qr_code',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
