# Generated by Django 2.0 on 2017-12-22 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0015_auto_20171219_0910'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoicedcustomer',
            name='notes',
            field=models.TextField(blank=True, verbose_name='Notes'),
        ),
    ]
