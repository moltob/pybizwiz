# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 12:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20161219_0934'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'verbose_name': 'Article', 'verbose_name_plural': 'Articles'},
        ),
        migrations.AlterField(
            model_name='article',
            name='inactive',
            field=models.BooleanField(default=False, help_text='Inactive articles can no longer be used in projects and invoices.', verbose_name='No longer used.'),
        ),
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(max_length=128, unique=True, verbose_name='Invoice text'),
        ),
        migrations.AlterField(
            model_name='article',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Unit price'),
        ),
    ]
