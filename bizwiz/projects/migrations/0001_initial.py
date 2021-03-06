# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-05 12:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('customers', models.ManyToManyField(to='customers.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('start_date', models.DateField(auto_now=True, verbose_name='Start date')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
            ],
        ),
        migrations.AddField(
            model_name='customergroup',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project'),
        ),
    ]
