# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-23 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_ern_burn', '0016_earnactiondetail_terms_and_conditions'),
    ]

    operations = [
        migrations.AddField(
            model_name='earnactiondetail',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='shop_category'),
        ),
    ]