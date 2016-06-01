from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from allonsy_main.models import Account, Organization, Location, User, UserExtension, RelationOrganizationUser, UserExtension, UserProfile, UserInteraction


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


class DoSendReplyMessage(ModelForm):
    class Meta:
        model = UserInteraction
        fields = ['interaction_subject', 'interaction_text']


class DoEditUserProfile(forms.Form):
    profile_aboutme = forms.CharField(max_length=5000)


class DoEditUserInfoContact(forms.Form):
    user_name_alias = forms.CharField(max_length=100)
    user_personal_email_value = forms.EmailField(max_length=100)
    user_country_id = forms.CharField(max_length=2)
    user_city_name = forms.CharField(max_length=100)
    user_province_name = forms.CharField(max_length=100)
    user_PostalCode = forms.CharField(max_length=10)
    user_home_street_number = forms.CharField(max_length=100)
    user_home_street_name = forms.CharField(max_length=100)
    user_home_ApartmentNumber = forms.CharField(max_length=16)
    user_phone_CountryCode = forms.CharField(max_length=3)
    user_phone_value = forms.CharField(max_length=100)
    user_phone_home_CountryCode = forms.CharField(max_length=3)
    user_phone_home_value = forms.CharField(max_length=100)


class DoEditUserEmergencyContact(forms.Form):
    emergency_contact_1_name = forms.CharField(max_length=100)
    emergency_contact_1_personal_email_value = forms.EmailField(max_length=100)
    emergency_contact_1_country_id = forms.CharField(max_length=2)
    emergency_contact_1_city_name = forms.CharField(max_length=100)
    emergency_contact_1_province_name = forms.CharField(max_length=100)
    emergency_contact_1_PostalCode = forms.CharField(max_length=10)
    emergency_contact_1_home_street_number = forms.CharField(max_length=100)
    emergency_contact_1_home_street_name = forms.CharField(max_length=100)
    emergency_contact_1_home_ApartmentNumber = forms.CharField(max_length=16)
    emergency_contact_1_phone_home_CountryCode = forms.CharField(max_length=3)
    emergency_contact_1_phone_home_value = forms.CharField(max_length=100)
    emergency_contact_2_name = forms.CharField(max_length=100)
    emergency_contact_2_personal_email_value = forms.EmailField(max_length=100)
    emergency_contact_2_country_id = forms.CharField(max_length=2)
    emergency_contact_2_city_name = forms.CharField(max_length=100)
    emergency_contact_2_province_name = forms.CharField(max_length=100)
    emergency_contact_2_PostalCode = forms.CharField(max_length=10)
    emergency_contact_2_home_street_number = forms.CharField(max_length=100)
    emergency_contact_2_home_street_name = forms.CharField(max_length=100)
    emergency_contact_2_home_ApartmentNumber = forms.CharField(max_length=16)
    emergency_contact_2_phone_home_CountryCode = forms.CharField(max_length=3)
    emergency_contact_2_phone_home_value = forms.CharField(max_length=100)


class DoAssocOrganization(forms.Form):
    parent = forms.CharField(max_length=100)
    child = forms.CharField(max_length=100)


class DoAssocOrganizationUser(forms.Form):
    org = forms.CharField(max_length=100)
    user = forms.CharField(max_length=100)



