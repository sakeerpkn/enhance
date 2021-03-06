# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-27 08:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_ern_burn', '0022_auto_20180326_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='burnactiondetail',
            name='validity_type',
            field=models.CharField(choices=[('Date', 'Date'), ('Period', 'Period'), ('No Validity', 'No Validity')], default='Date', max_length=6),
        ),
        migrations.AlterField(
            model_name='earnactiondetail',
            name='validity_type',
            field=models.CharField(choices=[('Date', 'Date'), ('Period', 'Period'), ('No Validity', 'No Validity')], max_length=20),
        ),
    ]
