# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-23 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_auto_20180323_0649'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageGallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=512, null=True)),
                ('image_type', models.IntegerField(choices=[(0, 'images'), (1, 'Banner image')], default=0)),
                ('image', models.ImageField(blank=True, null=True, upload_to='image_gallery')),
                ('tag', models.CharField(blank=True, max_length=256, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='ImagesGallery',
        ),
    ]
