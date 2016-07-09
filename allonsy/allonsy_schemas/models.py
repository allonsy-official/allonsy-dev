import uuid, random

from django.db import models

from django.contrib.auth.models import Group, User

from mptt.models import MPTTModel, TreeForeignKey

from tenant_schemas.models import TenantMixin


# Create your models here.
class Account (TenantMixin):

    randomset = random.randint(1, 100)

    uuid_account = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: Remove default val for account_name, account_institution_name before production
    account_name = models.CharField(max_length=100, unique=True)
    account_institution_name = models.CharField(max_length=100, default="Example University")
    account_url_name = models.CharField(max_length=24)
    account_billing_title = models.CharField(max_length=100, default='TESTING')
    account_billing_attn = models.CharField(max_length=100, default='TESTING')
    account_billing_country_id = models.CharField(max_length=2, default="US")
    account_billing_province_name = models.CharField(max_length=100, default='TESTING')
    account_billing_city_name = models.CharField(max_length=100, default='TESTING')
    account_billing_PostalCode = models.CharField(max_length=10, default='TESTING')
    account_billing_street_number = models.CharField(max_length=100, default='TESTING')
    account_billing_street_name = models.CharField(max_length=100, default='TESTING')
    account_billing_ApartmentNumber = models.CharField(max_length=16, blank=True)
    account_billing_CountryCode = models.CharField(max_length=3, default='555')
    account_billing_phone_value = models.CharField(max_length=10, default='TESTING')
    date_added = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    def __str__(self):
        return self.account_name
