# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-10 06:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_auto_20170105_1352'),
        ('projects', '0004_auto_20170105_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='articles',
            field=models.ManyToManyField(to='articles.Article'),
        ),
    ]
