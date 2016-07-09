from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from allonsy_main.models import Organization, Location, User, UserExtension, RelationOrganizationUser, UserExtension, UserProfile, UserInteraction
from allonsy_schemas.models import Account


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


class DoAddLocation(forms.Form):
    location_HasParent = forms.CharField(max_length=8, required=False)
    location_InheritGeoFromParent = forms.CharField(max_length=8, required=False)
    location_type = forms.CharField(max_length=1)
    location_SubLocIdent = forms.CharField(max_length=16)
    location_FullName = forms.CharField(max_length=100)
    location_ShortName = forms.CharField(max_length=32)
    location_abbreviation = forms.CharField(max_length=8)
    location_country_id = forms.CharField(max_length=2)
    location_province_name = forms.CharField(max_length=100)
    location_city_name = forms.CharField(max_length=100)
    location_PostalCode = forms.CharField(max_length=10)
    location_street_number = forms.CharField(max_length=100)
    location_street_name = forms.CharField(max_length=100)
    location_ApartmentNumber = forms.CharField(max_length=16)
    location_CountryCode = forms.CharField(max_length=3)
    location_phone_value = forms.CharField(max_length=10)

    def clean_HasParent(self):
        location_HasParent = self.cleaned_data['location_HasParent']
        if location_HasParent == 'on':
            location_HasParent = True
        else:
            location_HasParent = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return location_HasParent

    def clean_InheritGeoFromParent(self):
        location_InheritGeoFromParent = self.cleaned_data['location_InheritGeoFromParent']
        if location_InheritGeoFromParent == 'on':
            location_InheritGeoFromParent = True
        else:
            location_InheritGeoFromParent = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return location_InheritGeoFromParent


'''class DoAddUser(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']'''


class DoUserConnect(forms.Form):
    interaction_text = forms.CharField(max_length=500, required=False)
    relation_type = forms.CharField(max_length=500)

    def clean_interaction_text(self):
        interaction_text = self.cleaned_data['interaction_text']
        if interaction_text == '':
            interaction_text = 'Please add me as a connection.'
        else:
            interaction_text = self.cleaned_data['interaction_text']
        # Always return the cleaned data, whether you have changed it or
        # not.
        return interaction_text


class DoSendReplyMessage(ModelForm):
    class Meta:
        model = UserInteraction
        fields = ['interaction_subject', 'interaction_text']


class DoEditUserProfile(forms.Form):
    profile_aboutme = forms.CharField(max_length=5000)


class DoAddUser(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
    conf_password = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    is_superuser = forms.CharField(max_length=10, required=False)
    is_staff = forms.CharField(max_length=10, required=False)

    def clean_is_superuser(self):
        is_superuser = self.cleaned_data['is_superuser']
        if is_superuser == 'on':
            is_superuser = True
        else:
            is_superuser = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return is_superuser

    def clean_is_staff(self):
        location_is_staff = self.cleaned_data['is_staff']
        if location_is_staff == 'on':
            location_is_staff = True
        else:
            location_is_staff = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return location_is_staff


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



