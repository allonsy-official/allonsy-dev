# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-08 23:24
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('allonsy_main', '0008_userinteraction_uuid_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationuserconnection',
            name='uuid_relation',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
