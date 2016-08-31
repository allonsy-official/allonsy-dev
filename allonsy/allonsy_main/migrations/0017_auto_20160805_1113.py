# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-05 15:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allonsy_main', '0016_auto_20160804_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowtree',
            name='wf_item_is_proto',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='workflowtree',
            name='wf_item_name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
