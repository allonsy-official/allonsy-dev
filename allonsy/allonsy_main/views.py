from django.shortcuts import render, render_to_response, RequestContext, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Q
from django_ajax.decorators import ajax

from allonsy_main.forms import DoAddAccount, DoAddOrganization, DoAddLocation, DoAssocOrganization, DoAssocOrganizationUser, DoEditUserProfile, DoEditUserInfoContact, DoEditUserEmergencyContact
from allonsy_main.models import UserExtension, User, UserProfile, Organization, TreeOrganization, RelationOrganizationUser, UserInteraction


#create user_passes_check decorators here


# Create your views here.
def do_login(request):

    context = RequestContext(request)

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/user/'+str(user))
            else:
                # Return a 'disabled account' error message
                return HttpResponse("Disabled")

        else:
            # Return an 'invalid login' error message.
            return HttpResponse("Invalid login")

    else:
        return render_to_response('/app/', {}, context)


def do_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def user_admin(request):
    return render(request, 'allonsy/admin-base.html')


@login_required
def usr(request):
    current_user = request.user
    current_user_id = current_user.id
    user_extension = UserExtension.objects.get(user=current_user_id)
    user_phone = user_extension.user_phone_value
    context_dict = {'user_extension': user_phone, }
    return render(request, 'allonsy/user.html', context_dict)


@login_required
def resolve_user_url(request, username):
    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_user_acct = req_userextension.uuid_account
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)
    context_dict = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme}
    # return render(request, 'allonsy/user.html', context_dict)

    if current_user_acct == req_user_acct:

        return render(request, 'allonsy/user.html', context_dict, context_instance=RequestContext(request))

    else:
        # Return a 'disabled account' error message
        return HttpResponse("Disabled")


@login_required
def edit_user_url(request, username):
    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_user_acct = req_userextension.uuid_account
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)
    context_dict = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme}
    # return render(request, 'allonsy/user.html', context_dict)

    if current_user_acct == req_user_acct:

        return render(request, 'allonsy/forms/edituser.html', context_dict, context_instance=RequestContext(request))

    else:
        # Return a 'disabled account' error message
        return HttpResponse("Disabled")

@login_required
def resolve_org_url(request, orgname):
    current_user = request.user
    current_user_id = current_user.id
    current_user_userextension = UserExtension.objects.get(user=current_user_id)
    current_user_uuid = current_user_userextension.uuid_user
    current_user_auth = 'True'
    #TODO: Add auth that user is allowed to see this group and/or interact
    org_short_name = orgname.replace('-', ' ')
    context_dict = {'current_user': current_user, 'current_user_auth': current_user_auth, 'org_short_name': org_short_name}
    return render(request, 'allonsy/org.html', context_dict, context_instance=RequestContext(request))

@login_required
def create(request):
    return render(request, 'allonsy/create.html',)


@login_required
def create_account(request):
    return render(request, 'allonsy/account.html',)


@login_required
def create_organization(request):
    return render(request, 'allonsy/organization.html',)


@login_required
def create_location(request):
    return render(request, 'allonsy/location.html',)


@login_required
def do_add_account(request):
    do_add_account_form = DoAddAccount(request.POST)
    if request.method == 'POST':
        if do_add_account_form.is_valid():
            account_name = do_add_account_form.cleaned_data['account_name']
            account_institution_name = do_add_account_form.cleaned_data['account_institution_name']
            account_billing_title = do_add_account_form.cleaned_data['account_billing_title']
            account_billing_attn = do_add_account_form.cleaned_data['account_billing_attn']
            account_billing_country_id = do_add_account_form.cleaned_data['account_billing_country_id']
            account_billing_province_name = do_add_account_form.cleaned_data['account_billing_province_name']
            account_billing_city_name = do_add_account_form.cleaned_data['account_billing_city_name']
            account_billing_PostalCode = do_add_account_form.cleaned_data['account_billing_PostalCode']
            account_billing_street_number = do_add_account_form.cleaned_data['account_billing_street_number']
            account_billing_street_name = do_add_account_form.cleaned_data['account_billing_street_name']
            account_billing_ApartmentNumber = do_add_account_form.cleaned_data['account_billing_ApartmentNumber']
            account_billing_CountryCode = do_add_account_form.cleaned_data['account_billing_CountryCode']
            account_billing_phone_value = do_add_account_form.cleaned_data['account_billing_phone_value']

            do_add_account_form.save()

            return render(request, 'allonsy/user.html')

        else:
                # Return a 'disabled account' error message
                return render_to_response('allonsy/account.html', {'form': do_add_account_form})

    else:
            # Return a 'disabled account' error message
        return render_to_response('allonsy/account.html', {'form': do_add_account_form})


@login_required
def do_add_organization(request):
    do_add_organization_form = DoAddOrganization(request.POST)
    if request.method == 'POST':
        fk_val = request.user.userextension.uuid_account
        if do_add_organization_form.is_valid():
            org_FullName = do_add_organization_form.cleaned_data['org_FullName']
            org_ShortName = do_add_organization_form.cleaned_data['org_ShortName']
            org_abbreviation = do_add_organization_form.cleaned_data['org_abbreviation']
            org_type = do_add_organization_form.cleaned_data['org_type']
            org_HasParent = do_add_organization_form.cleaned_data['org_HasParent']

            proto_form = do_add_organization_form.save(commit=False)

            proto_form.uuid_account = fk_val

            proto_form.save()

            return render(request, 'allonsy/user.html')

        else:
                # Return a 'disabled account' error message
                return render_to_response('allonsy/organization.html', {'form': do_add_organization_form})

    else:
            # Return a 'disabled account' error message
        return render_to_response('allonsy/organization.html', {'form': do_add_organization_form})


@login_required
def assoc_organization(request):
    orglist = Organization.objects.all().filter(uuid_account=request.user.userextension.uuid_account)
    return render(request, 'allonsy/associate-org.html', {'orgs': orglist}, context_instance=RequestContext(request))


@login_required
def do_assoc_organization(request):
    #TODO: Handle exception when user attempts to assign same org as child. Should pop error modal and ask if sure user wishes to move the node. Modify node.parent to complete.
    do_assoc_organization_form = DoAssocOrganization(request.POST)
    if request.method == 'POST':
        fk_val = request.user.userextension.uuid_account
        if do_assoc_organization_form.is_valid():
            parent = do_assoc_organization_form.cleaned_data['parent']
            child = do_assoc_organization_form.cleaned_data['child']

            org_parent = Organization.objects.get(uuid_org=parent)
            org_child = Organization.objects.get(uuid_org=child)

            if TreeOrganization.objects.filter(uuid_org=org_parent).exists():

                tree_org_parent = TreeOrganization.objects.get(uuid_org=parent)

                TreeOrganization.objects.create(relation_name=org_child, uuid_account=fk_val, uuid_org=org_child, parent=tree_org_parent)

            else:
                TreeOrganization.objects.create(uuid_account=fk_val, uuid_org=org_parent)

                tree_org_parent = TreeOrganization.objects.get(uuid_org=parent)

                TreeOrganization.objects.create(relation_name=org_child, uuid_account=fk_val, uuid_org=org_child, parent=tree_org_parent)

            return render(request, 'allonsy/user.html')

        else:
            # Return a 'disabled account' error message
            return render_to_response('allonsy/organization.html', {'form': do_assoc_organization_form})

    else:
            # Return a 'disabled account' error message
        return render_to_response('allonsy/organization.html', {'form': do_assoc_organization_form})


@login_required
def assoc_organization_user(request):
    orglist = Organization.objects.all().filter(uuid_account=request.user.userextension.uuid_account)
    usrlist = UserExtension.objects.all().filter(uuid_account=request.user.userextension.uuid_account)
    return render(request, 'allonsy/associate-user.html', {'orgs': orglist, 'users': usrlist}, context_instance=RequestContext(request))


@login_required
def do_assoc_organization_user(request):
    #TODO: Handle exception when user attempts to assign same org as child. Should pop error modal and ask if sure user wishes to move the node. Modify node.parent to complete.
    do_assoc_organization_user_form = DoAssocOrganizationUser(request.POST)
    if request.method == 'POST':
        fk_val = request.user.userextension.uuid_account
        if do_assoc_organization_user_form.is_valid():
            org = do_assoc_organization_user_form.cleaned_data['org']
            usr = do_assoc_organization_user_form.cleaned_data['user']

            assoc_org = Organization.objects.get(uuid_org=org)
            assoc_usr = UserExtension.objects.get(uuid_user=usr)
            assoc_usr_lookup = User.objects.get(username=assoc_usr.user)
            assoc_org_name = assoc_org.org_FullName
            assoc_usr_name = assoc_usr_lookup.username
            assoc_relation_name = assoc_org_name

            if RelationOrganizationUser.objects.filter(relation_name=assoc_relation_name, uuid_account=fk_val).exists():

                return HttpResponse('User already exists in group')

            else:
                #TODO: Create elif to check if user already is associated with org, rather than simply if user exists as in above
                do_create_object = RelationOrganizationUser.objects.create(uuid_account=fk_val, relation_name=assoc_relation_name)
                #many-to-many only after object created
                do_create_object.save()
                do_create_object.uuid_org.add(assoc_org)
                do_create_object.uuid_user.add(usr)

            return render('allonsy/user.html')

        else:
            # Return a 'disabled account' error message
            return render_to_response('allonsy/associate-user.html', {'form': do_assoc_organization_user_form})
            # return HttpResponse('Fail 1')

    else:
            # Return a 'disabled account' error message
       #return render_to_response('allonsy/associate-user.html', {'form': do_assoc_organization_user_form})
        return HttpResponse('Fail 2')

@login_required
def do_get_user_interactions(request, username):
    current_user = User.objects.get(username=request.user)
    new_user_interactions = UserInteraction.objects.all().filter(interaction_target=current_user, interaction_status='O')
    count_new_user_interactions = new_user_interactions.count
    current_user_interactions = UserInteraction.objects.all()
    #current_user_interactions = UserInteraction.objects.all().filter(Q(interaction_target=current_user), Q(interaction_status='O') | Q(interaction_status='I'))

    context_dict = {'cur_user': current_user, 'cur_user_interacts': current_user_interactions, 'count_new_user_interactions': count_new_user_interactions}

    return render(request, 'allonsy/interactions.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_edit_user_profile(request, username):
    do_edit_user_profile_form = DoEditUserProfile(request.POST)

    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_user_acct = req_userextension.uuid_account
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)

    context_dict = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme}

    if request.method == 'POST':
        if do_edit_user_profile_form.is_valid():
            profile_aboutme = do_edit_user_profile_form.cleaned_data['profile_aboutme']

            do_edit_profile_object = UserProfile.objects.get(uuid_user=req_userextension)
            do_edit_profile_object.profile_aboutme = profile_aboutme
            do_edit_profile_object.save()

            return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

        else:
            return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

    else:
            # Return a 'disabled account' error message
        return render(request, 'allonsy/forms/edituser.html', context_dict, context_instance=RequestContext(request))

@login_required
def do_edit_user_info_contact(request, username):
    do_edit_user_info_contact_form = DoEditUserInfoContact(request.POST)

    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_user_acct = req_userextension.uuid_account
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)

    context_dict = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme}

    if request.method == 'POST':
        if do_edit_user_info_contact_form.is_valid():
            user_name_alias = do_edit_user_info_contact_form.cleaned_data['user_name_alias']
            user_phone_CountryCode = do_edit_user_info_contact_form.cleaned_data['user_phone_CountryCode']
            user_phone_value = do_edit_user_info_contact_form.cleaned_data['user_phone_value']
            user_personal_email_value = do_edit_user_info_contact_form.cleaned_data['user_personal_email_value']
            user_phone_home_CountryCode = do_edit_user_info_contact_form.cleaned_data['user_phone_home_CountryCode']
            user_phone_home_value = do_edit_user_info_contact_form.cleaned_data['user_phone_home_value']
            user_home_street_number = do_edit_user_info_contact_form.cleaned_data['user_home_street_number']
            user_home_street_name = do_edit_user_info_contact_form.cleaned_data['user_home_street_name']
            user_home_ApartmentNumber = do_edit_user_info_contact_form.cleaned_data['user_home_ApartmentNumber']
            user_country_id = do_edit_user_info_contact_form.cleaned_data['user_country_id']
            user_PostalCode = do_edit_user_info_contact_form.cleaned_data['user_PostalCode']
            user_city_name = do_edit_user_info_contact_form.cleaned_data['user_city_name']
            user_province_name = do_edit_user_info_contact_form.cleaned_data['user_province_name']

            do_edit_userextension_object = UserExtension.objects.get(uuid_user=req_userextension.uuid_user)

            do_edit_userextension_object.user_name_alias = user_name_alias
            do_edit_userextension_object.user_phone_CountryCode = user_phone_CountryCode
            do_edit_userextension_object.user_phone_value = user_phone_value
            do_edit_userextension_object.user_personal_email_value = user_personal_email_value
            do_edit_userextension_object.user_phone_home_CountryCode = user_phone_home_CountryCode
            do_edit_userextension_object.user_phone_home_value = user_phone_home_value
            do_edit_userextension_object.user_home_street_number = user_home_street_number
            do_edit_userextension_object.user_home_street_name = user_home_street_name
            do_edit_userextension_object.user_home_ApartmentNumber = user_home_ApartmentNumber
            do_edit_userextension_object.user_country_id = user_country_id
            do_edit_userextension_object.user_PostalCode = user_PostalCode
            do_edit_userextension_object.user_city_name = user_city_name
            do_edit_userextension_object.user_province_name = user_province_name

            do_edit_userextension_object.save()

            return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

        else:
            #return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))
            return HttpResponse('Fail 2')

    else:
            # Return a 'disabled account' error message
        return render(request, 'allonsy/forms/editusercontacts.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_edit_user_emergency_contact(request, username):
    do_edit_user_emergency_contact_form = DoEditUserEmergencyContact(request.POST)

    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_user_acct = req_userextension.uuid_account
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)
    error_dict = {}
    context_dict = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme,
                    'do_edit_user_emergency_contact_form': do_edit_user_emergency_contact_form}

    if request.method == 'POST':
        if do_edit_user_emergency_contact_form.is_valid():
            emergency_contact_1_name = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_name']
            emergency_contact_1_personal_email_value = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_personal_email_value']
            emergency_contact_1_phone_home_CountryCode = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_phone_home_CountryCode']
            emergency_contact_1_phone_home_value = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_phone_home_value']
            emergency_contact_1_home_street_number = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_home_street_number']
            emergency_contact_1_home_street_name = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_home_street_name']
            emergency_contact_1_home_ApartmentNumber = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_home_ApartmentNumber']
            emergency_contact_1_country_id = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_country_id']
            emergency_contact_1_PostalCode = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_PostalCode']
            emergency_contact_1_city_name = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_city_name']
            emergency_contact_1_province_name = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_1_province_name']
            emergency_contact_2_name = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_name']
            emergency_contact_2_personal_email_value = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_personal_email_value']
            emergency_contact_2_phone_home_CountryCode = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_phone_home_CountryCode']
            emergency_contact_2_phone_home_value = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_phone_home_value']
            emergency_contact_2_home_street_number = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_home_street_number']
            emergency_contact_2_home_street_name = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_home_street_name']
            emergency_contact_2_home_ApartmentNumber = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_home_ApartmentNumber']
            emergency_contact_2_country_id = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_country_id']
            emergency_contact_2_PostalCode = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_PostalCode']
            emergency_contact_2_city_name = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_city_name']
            emergency_contact_2_province_name = do_edit_user_emergency_contact_form.cleaned_data['emergency_contact_2_province_name']

            do_edit_user_profile_object = UserProfile.objects.get(uuid_user=req_userextension.uuid_user)

            do_edit_user_profile_object.emergency_contact_2_name = emergency_contact_2_name
            do_edit_user_profile_object.emergency_contact_2_phone_home_CountryCode = emergency_contact_2_phone_home_CountryCode
            do_edit_user_profile_object.emergency_contact_2_phone_home_value = emergency_contact_2_phone_home_value
            do_edit_user_profile_object.emergency_contact_2_home_street_number = emergency_contact_2_home_street_number
            do_edit_user_profile_object.emergency_contact_2_home_street_name = emergency_contact_2_home_street_name
            do_edit_user_profile_object.emergency_contact_2_home_ApartmentNumber = emergency_contact_2_home_ApartmentNumber
            do_edit_user_profile_object.emergency_contact_2_country_id = emergency_contact_2_country_id
            do_edit_user_profile_object.emergency_contact_2_PostalCode = emergency_contact_2_PostalCode
            do_edit_user_profile_object.emergency_contact_2_city_name = emergency_contact_2_city_name
            do_edit_user_profile_object.emergency_contact_2_province_name = emergency_contact_2_province_name
            do_edit_user_profile_object.emergency_contact_2_personal_email_value = emergency_contact_2_personal_email_value

            do_edit_user_profile_object.emergency_contact_1_name = emergency_contact_1_name
            do_edit_user_profile_object.emergency_contact_1_phone_home_CountryCode = emergency_contact_1_phone_home_CountryCode
            do_edit_user_profile_object.emergency_contact_1_phone_home_value = emergency_contact_1_phone_home_value
            do_edit_user_profile_object.emergency_contact_1_home_street_number = emergency_contact_1_home_street_number
            do_edit_user_profile_object.emergency_contact_1_home_street_name = emergency_contact_1_home_street_name
            do_edit_user_profile_object.emergency_contact_1_home_ApartmentNumber = emergency_contact_1_home_ApartmentNumber
            do_edit_user_profile_object.emergency_contact_1_country_id = emergency_contact_1_country_id
            do_edit_user_profile_object.emergency_contact_1_PostalCode = emergency_contact_1_PostalCode
            do_edit_user_profile_object.emergency_contact_1_city_name = emergency_contact_1_city_name
            do_edit_user_profile_object.emergency_contact_1_province_name = emergency_contact_1_province_name
            do_edit_user_profile_object.emergency_contact_1_personal_email_value = emergency_contact_1_personal_email_value

            do_edit_user_profile_object.save()

            return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

        else:
            do_edit_user_emergency_contact_form = DoEditUserProfile()
            error_dict['form'] = do_edit_user_emergency_contact_form

            return render(request, 'allonsy/forms/edituseremergencycontacts.html', context_dict, context_instance=RequestContext(request))

    else:
            # Return a 'disabled account' error message

        return render(request, 'allonsy/forms/edituseremergencycontacts.html', context_dict, context_instance=RequestContext(request))


def app(request):
    return render(request, 'allonsy/app.html')
