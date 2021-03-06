# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-26 05:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_user', '0011_auto_20180226_0836'),
        ('customer', '0004_auto_20180323_0957'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.TextField()),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('mobile', models.CharField(blank=True, max_length=20, null=True)),
                ('state', models.IntegerField(choices=[(0, 'Received'), (1, 'Approved'), (2, 'Rejected'), (2, 'Sent Response')], default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api_user.CustomerDetail')),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='customer_query_type', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerQueryType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='category_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='query_category_modified', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='imagegallery',
            name='image_type',
            field=models.IntegerField(choices=[(0, 'image'), (1, 'Banner image'), (2, 'Newsfeed image'), (3, 'Newsfeed Banner image')], default=0),
        ),
        migrations.AddField(
            model_name='customerquery',
            name='query_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.CustomerQueryType'),
        ),
    ]
