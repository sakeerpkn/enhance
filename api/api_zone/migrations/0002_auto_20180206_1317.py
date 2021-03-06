# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-06 07:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_baggage', '0003_customerbag_shelf'),
        ('api_zone', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZoneToZoneManagerMapping',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1046)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('status', models.IntegerField(default=1)),
                ('created_user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='zone_mapping_created_user_id', to=settings.AUTH_USER_MODEL)),
                ('manager_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('modified_user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='zone_mapping_modified_user_id', to=settings.AUTH_USER_MODEL)),
                ('zone_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api_baggage.Location')),
            ],
            options={
                'verbose_name_plural': 'zone_manager_mapping',
            },
        ),
        migrations.RemoveField(
            model_name='shelf',
            name='location_id',
        ),
        migrations.AddField(
            model_name='shelf',
            name='zone_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api_baggage.Location'),
        ),
    ]
