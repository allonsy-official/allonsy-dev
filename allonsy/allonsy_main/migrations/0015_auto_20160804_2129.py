# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-05 01:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('allonsy_main', '0014_auto_20160804_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflowtree',
            name='uuid_meta',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='meta', to='allonsy_main.WFMetaData'),
        ),
    ]
