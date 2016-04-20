# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-15 12:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('reversion', '0007_auto_20160415_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='revision',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, db_index=True, default=datetime.datetime(2016, 4, 15, 12, 59, 53, 525000, tzinfo=utc), help_text='The date and time this revision was updated.', verbose_name='date updated'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='version',
            name='status',
            field=models.IntegerField(choices=[(2, 'Approved'), (1, 'Pending'), (-1, 'Rejected')], default=1),
        ),
    ]