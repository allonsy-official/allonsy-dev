# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-16 15:47
from __future__ import unicode_literals

from django.db import migrations, models
import tenant_schemas.postgresql_backend.base
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('domain_url', models.CharField(max_length=128, unique=True)),
                ('schema_name', models.CharField(max_length=63, unique=True, validators=[tenant_schemas.postgresql_backend.base._check_schema_name])),
                ('uuid_account', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('account_name', models.CharField(max_length=100, unique=True)),
                ('account_institution_name', models.CharField(default='Example University', max_length=100)),
                ('account_url_name', models.CharField(max_length=24)),
                ('account_billing_title', models.CharField(default='TESTING', max_length=100)),
                ('account_billing_attn', models.CharField(default='TESTING', max_length=100)),
                ('account_billing_country_id', models.CharField(default='US', max_length=2)),
                ('account_billing_province_name', models.CharField(default='TESTING', max_length=100)),
                ('account_billing_city_name', models.CharField(default='TESTING', max_length=100)),
                ('account_billing_PostalCode', models.CharField(default='TESTING', max_length=10)),
                ('account_billing_street_number', models.CharField(default='TESTING', max_length=100)),
                ('account_billing_street_name', models.CharField(default='TESTING', max_length=100)),
                ('account_billing_ApartmentNumber', models.CharField(blank=True, max_length=16)),
                ('account_billing_CountryCode', models.CharField(default='555', max_length=3)),
                ('account_billing_phone_value', models.CharField(default='TESTING', max_length=10)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_edited', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
