# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-20 02:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('allonsy_main', '0026_auto_20160519_2156'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='emergency_contact_1_hone_home_CountryCode',
            new_name='emergency_contact_1_phone_home_CountryCode',
        ),
    ]
