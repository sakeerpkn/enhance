# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-26 06:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0016_shop_logo'),
        ('api_ern_burn', '0018_auto_20180326_0642'),
    ]

    operations = [
        migrations.AddField(
            model_name='burnactiondetail',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='burn_coupons', to='base_app.Shop'),
        ),
    ]