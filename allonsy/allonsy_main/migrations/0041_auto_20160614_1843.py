# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-14 22:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allonsy_main', '0040_auto_20160614_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_url_name',
            field=models.CharField(max_length=24),
        ),
    ]
