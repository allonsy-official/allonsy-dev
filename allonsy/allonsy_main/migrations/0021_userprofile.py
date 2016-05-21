# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-16 14:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('allonsy_main', '0020_auto_20160516_1053'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_aboutme', models.TextField(default='This user has not added any text!')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('uuid_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='allonsy_main.UserExtension')),
            ],
        ),
    ]
