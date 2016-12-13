from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from allonsy_main.models import Organization, Location, User, UserExtension, RelationOrganizationUser, UserExtension, UserProfile, UserInteractionTree, WorkflowTree
from allonsy_schemas.models import Account


class DoAddAccount(ModelForm):
    class Meta:
        model = Account
        fields = ['account_name', 'account_institution_name', 'account_billing_title', 'account_billing_attn',
                  'account_billing_country_id', 'account_billing_province_name', 'account_billing_city_name',
                  'account_billing_PostalCode', 'account_billing_street_number', 'account_billing_street_name',
                  'account_billing_ApartmentNumber', 'account_billing_CountryCode', 'account_billing_phone_value']


class DoAddOrganization(forms.Form):
    org_parent = forms.CharField(max_length=64)
    org_FullName = forms.CharField(max_length=100)
    org_ShortName = forms.CharField(max_length=32)
    org_abbreviation = forms.CharField(max_length=8)
    org_type = forms.CharField(max_length=1)
    org_type_special = forms.CharField(max_length=8, required=False)


class DoAddLocation(forms.Form):
    location_parent = forms.CharField(max_length=64)
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

    def clean_InheritGeoFromParent(self):
        location_InheritGeoFromParent = self.cleaned_data['location_InheritGeoFromParent']
        if location_InheritGeoFromParent == 'on':
            location_InheritGeoFromParent = True
        else:
            location_InheritGeoFromParent = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return location_InheritGeoFromParent


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
        model = UserInteractionTree
        fields = ['interaction_subject', 'interaction_text']


class DoSendMessage(ModelForm):
    class Meta:
        model = UserInteractionTree
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


class DoAddEditWFSet(forms.Form):
    wf_set_name = forms.CharField(max_length=64)
    wf_set_is_type = forms.CharField(max_length=1)
    wf_set_is_default_parent_for_type = forms.CharField(max_length=16, required=False)
    wf_set_is_active = forms.CharField(max_length=16, required=False)
    wf_set_has_child = forms.CharField(max_length=16, required=False)

    def clean_wf_item_is_active(self):
        wf_item_is_active = self.cleaned_data['wf_item_is_active']
        if wf_item_is_active == 'True':
            wf_item_is_active = True
        else:
            wf_item_is_active = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return wf_item_is_active

    def clean_wf_set_is_default_parent_for_type(self):
        wf_set_is_default_parent_for_type = self.cleaned_data['wf_set_is_default_parent_for_type']
        if wf_set_is_default_parent_for_type == 'True':
            wf_set_is_default_parent_for_type = True
        else:
            wf_set_is_default_parent_for_type = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return wf_set_is_default_parent_for_type

    def clean_wf_set_has_child(self):
        wf_set_has_child = self.cleaned_data['wf_set_has_child']
        if wf_set_has_child == 'True':
            wf_set_has_child = True
        else:
            wf_set_has_child = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return wf_set_has_child


class DoAddEditWFChild(forms.Form):
    wf_set_name = forms.CharField(max_length=64)
    wf_disp_order = forms.CharField(max_length=2)
    wf_set_is_active = forms.CharField(max_length=16, required=False)

    def clean_wf_set_is_active(self):
        wf_set_is_active = self.cleaned_data['wf_set_is_active']
        if wf_set_is_active == 'True':
            wf_set_is_active = True
        else:
            wf_set_is_active = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return wf_set_is_active


class DoAddEditWFItem(forms.Form):
    wf_item_is_active = forms.CharField(max_length=16)
    wf_item_name = forms.CharField(max_length=64)
    wf_item_text = forms.CharField(max_length=256)
    wf_item_disp_order = forms.CharField(max_length=2)

    def clean_wf_item_is_active(self):
        wf_item_is_active = self.cleaned_data['wf_item_is_active']
        if wf_item_is_active == 'True':
            wf_item_is_active = True
        else:
            wf_item_is_active = False
        # Always return the cleaned data, whether you have changed it or
        # not.
        return wf_item_is_active


class DoAddEditWFTreeNode(forms.Form):
    wf_item_name = forms.CharField(max_length=32)
    wf_item_text = forms.CharField(max_length=256, required=False)
    wf_item_is_default = forms.CharField(max_length=8, required=False)
    wf_item_is_active = forms.CharField(max_length=8, required=False)
    proto_wf_doc_type = forms.CharField(max_length=32)


class DoAddEditWFTreeItem(forms.Form):
    wf_item_name = forms.CharField(max_length=32)
    wf_item_text = forms.CharField(max_length=256, required=False)
    wf_item_is_default = forms.CharField(max_length=8, required=False)
    wf_item_is_active = forms.CharField(max_length=8, required=False)
    proto_wf_doc_type = forms.CharField(max_length=32)


class DoGetWFTreeForAddItem(forms.Form):
    get_this_node_docs = forms.CharField(max_length=32)


class DoAddWFTreeItem(forms.Form):
    wf_item_name = forms.CharField(max_length=32)
    wf_item_text = forms.CharField(max_length=256, required=False)
    wf_item_is_active = forms.CharField(max_length=8, required=False)


class DoDeleteWFTreeItem(forms.Form):
    wf_item_do_delete = forms.CharField(max_length=8, required=False)


class DoGetWFInstance(forms.Form):

    def __init__(self, *args, **kwargs):
        dyn_items = kwargs.pop('dyn_items')
        super(DoGetWFInstance, self).__init__(*args, **kwargs)

        # for i, question in enumerate(dyn_items):
        for item in dyn_items:
            # self.fields['custom_%s' % i] = forms.BooleanField(label=question, required=False)
            self.fields[str(item.uuid_wf_item)] = forms.BooleanField(required=False)

    def extra_states(self):
        return self.cleaned_data.items()


class DoEditWFInstanceMeta(forms.Form):
    wf_item_name = forms.CharField(max_length=256)
    wf_item_text = forms.CharField(max_length=1024, required=False)


class DoAddEpoch(forms.Form):
    epoch_parent = forms.CharField(max_length=64)
    epoch_Name = forms.CharField(max_length=100)
    epoch_StartDate = forms.DateField()
    epoch_EndDate = forms.DateField()


class DoGetUserSelectForm(forms.Form):
    user_pk = forms.CharField(max_length=100)
    campus_uuid = forms.CharField(max_length=100)


class DoGetLocForm(forms.Form):
    uuid_location = forms.CharField(max_length=64)




