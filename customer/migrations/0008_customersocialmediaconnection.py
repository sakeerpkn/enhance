# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-28 12:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0007_merge_20180326_1036'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerSocialMediaConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connect_type', models.IntegerField(blank=True, choices=[(0, 'facebook'), (1, 'google'), (2, 'twitter'), (3, 'instagram')], null=True)),
                ('unique_string', models.CharField(blank=True, max_length=256, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_media_connection', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
