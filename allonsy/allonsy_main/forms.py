from django import forms
from django.forms import ModelForm
from allonsy_main.models import Account, Organization, Location, User, UserExtension, RelationOrganizationUser


class DoAddAccount(ModelForm):
    class Meta:
        model = Account
        fields = ['account_name', 'account_institution_name', 'account_billing_title', 'account_billing_attn',
                  'account_billing_country_id', 'account_billing_province_name', 'account_billing_city_name',
                  'account_billing_PostalCode', 'account_billing_street_number', 'account_billing_street_name',
                  'account_billing_ApartmentNumber', 'account_billing_CountryCode', 'account_billing_phone_value']


class DoAddOrganization(ModelForm):
    class Meta:
        model = Organization
        exclude = ['uuid_account', ]
        fields = ['org_FullName', 'org_ShortName', 'org_abbreviation', 'org_type', 'org_HasParent']


class DoAddLocation(ModelForm):
    class Meta:
        model = Location
        fields = ['location_HasParent', 'location_InheritGeoFromParent', 'location_type', 'location_SubLocIdent',
                  'location_FullName', 'location_ShortName', 'location_abbreviation', 'location_country_id',
                  'location_province_name', 'location_city_name', 'location_PostalCode', 'location_street_number',
                  'location_street_name', 'location_ApartmentNumber', 'location_CountryCode', 'location_phone_value']


class DoAssocOrganization(forms.Form):
    parent = forms.CharField(max_length=100)
    child = forms.CharField(max_length=100)


class DoAssocOrganizationUser(forms.Form):
    org = forms.CharField(max_length=100)
    user = forms.CharField(max_length=100)



