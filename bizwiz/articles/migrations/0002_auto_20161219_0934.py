# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-19 08:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]