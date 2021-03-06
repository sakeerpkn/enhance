# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-04-03 06:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_user', '0011_auto_20180226_0836'),
        ('customer', '0008_customersocialmediaconnection'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=256, null=True)),
                ('invite_type', models.IntegerField(choices=[(0, 'Message'), (1, 'Email')])),
                ('invite_status', models.CharField(choices=[('PENDING', 'PENDING'), ('SENT', 'SENT'), ('FAILED', 'FAILED')], default='PENDING', max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_user.CustomerDetail')),
            ],
        ),
        migrations.AlterField(
            model_name='customersocialmediaconnection',
            name='unique_string',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
