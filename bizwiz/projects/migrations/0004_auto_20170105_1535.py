# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-05 14:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20170105_1505'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customergroup',
            options={'verbose_name': 'Customer group', 'verbose_name_plural': 'Customer groups'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'verbose_name': 'Project', 'verbose_name_plural': 'Projects'},
        ),
    ]