# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-07 08:15
from __future__ import unicode_literals
from datetime import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reversion', '0003_revision_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='revision',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.now()),
            preserve_default=False,
        ),
    ]