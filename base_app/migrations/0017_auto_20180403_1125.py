# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-04-03 11:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0016_shop_logo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statuslevel',
            old_name='points_needed',
            new_name='slab_ends',
        ),
        migrations.AddField(
            model_name='membershiplevel',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='badge'),
        ),
        migrations.AddField(
            model_name='statuslevel',
            name='slab_starts',
            field=models.FloatField(default=0.0),
        ),
    ]
