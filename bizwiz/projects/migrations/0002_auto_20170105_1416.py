# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-05 13:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='start_date',
            field=models.DateField(default=datetime.date.today, verbose_name='Start date'),
        ),
    ]
