# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-07 07:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reversion', '0002_auto_20141216_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='revision',
            name='status',
            field=models.IntegerField(default=0, verbose_name='Revision status'),
        ),
    ]