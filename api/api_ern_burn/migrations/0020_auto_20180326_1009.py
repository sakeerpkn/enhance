# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-26 10:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_ern_burn', '0019_burnactiondetail_shop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earntransaction',
            name='erned_action',
            field=models.ForeignKey(db_column='action_id', default=0, on_delete=django.db.models.deletion.DO_NOTHING, related_name='erned_user_id', to='api_ern_burn.EarnActionDetail'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='earntransaction',
            unique_together=set([('user', 'erned_action')]),
        ),
    ]