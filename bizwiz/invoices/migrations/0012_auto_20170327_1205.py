# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0011_auto_20170321_0719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicedarticle',
            name='kind',
            field=models.CharField(blank=True, choices=[('ARTICLE', 'ARTICLE'), ('REBATE', 'REBATE')], default='ARTICLE', max_length=10, verbose_name='Kind'),
        ),
    ]
