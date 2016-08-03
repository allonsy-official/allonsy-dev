import uuid, random, copy, collections
from itertools import chain

from django.shortcuts import render, render_to_response, RequestContext, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Q
from django_ajax.decorators import ajax

from allonsy_main.forms import DoAddAccount, DoAddOrganization, DoAddLocation, DoAddUser, DoAssocOrganization, DoAssocOrganizationUser, DoEditUserProfile, DoEditUserInfoContact, DoEditUserEmergencyContact, DoUserConnect, DoSendReplyMessage, DoSendMessage, DoAddEditWFSet, DoAddEditWFChild, DoAddEditWFItem
from allonsy_main.models import UserExtension, User, UserProfile, Organization, TreeOrganization, RelationOrganizationUser, UserInteractionTree, UserAlert, Location, RelationUserConnection, WorkflowSet, RelationWorkflow, WorkflowItem, RelationWorkflow, WorkflowItem
from allonsy_schemas.models import Account


#Helper functions
#TODO: middleware?

def get_user_data(request, username):
    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_acct = req_userextension.uuid_account
    req_user_uuid = req_userextension.uuid_user

    context_helper = {'current_user_obj': current_user_obj,
                      'cur_user': current_user,
                      'current_userextension': current_userextension,
                      'current_user_acct': current_user_acct,
                      'req_user': req_user,
                      'req_userextension': req_userextension,
                      'req_user_acct': req_user_acct,
                      'req_user_uuid': req_user_uuid,
                      }

    return context_helper


def get_user_data_objects(request, username):
    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_acct = req_userextension.uuid_account
    req_user_uuid = req_userextension.uuid_user

    return current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid


#create user_passes_check decorators here
def data_privacy_check(User):
    current_user_id = User.id


def allonsy_dev_check(User):
    current_user_id = User.id
    user_extension_object = UserExtension.objects.get(user=current_user_id)
    user_type = user_extension_object.user_type

    if user_type == 'X':
        return True

    else:
        return False


def user_admin_check(User):
    current_user_id = User.id
    user_extension_object = UserExtension.objects.get(user=current_user_id)
    user_type = user_extension_object.user_type

    if user_type == 'A' or user_type == 'D':
        return True

    else:
        return False


def access_admin_check(User):

    if user_admin_check(User) or allonsy_dev_check(User):
        return True

    else:
        return False


# Create your views here.
def do_login(request):

    context = RequestContext(request)

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:

            if user.is_active:
                current_userextension = UserExtension.objects.get(user=user)
                current_user_acct = current_userextension.uuid_account

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

    username = request.user

    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    context_dict_local = {'orgs_primary': req_user_orgs_primary}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    if current_user_acct == req_user_acct:

        #TODO: CHANGE BACK TO USER
        return render(request, 'allonsy/user_admin_main.html', context_dict, context_instance=RequestContext(request))

    else:
        # Return a 'disabled account' error message
        return HttpResponse("Disabled")


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
    #TODO: Add check to see if user has already requested to connect. Filter for uuid2 on current user and uuid1 on requser
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)
    req_user_connects_1 = RelationUserConnection.objects.filter(Q(uuid_user_1=req_user) & Q(relation_status='A')).values_list('uuid_user_2', flat=True)
    req_user_connects_2 = RelationUserConnection.objects.filter(Q(uuid_user_2=req_user) & Q(relation_status='A')).values_list('uuid_user_1', flat=True)
    current_user_connects_1 = RelationUserConnection.objects.filter(Q(uuid_user_1=current_user) & Q(relation_status='A')).values_list('uuid_user_2', flat=True)
    current_user_connects_2 = RelationUserConnection.objects.filter(Q(uuid_user_2=current_user) & Q(relation_status='A')).values_list('uuid_user_1', flat=True)
    # connects = list(chain(req_user_connects_1, req_user_connects_2, current_user_connects_1, current_user_connects_2))
    connects = set(chain(req_user_connects_1, req_user_connects_2, current_user_connects_1, current_user_connects_2))

    # Set status of connect button when visiting profile of another user
    if RelationUserConnection.objects.all().filter(uuid_user_1=current_user, uuid_user_2=req_user).exists():
        relation_status = RelationUserConnection.objects.get(uuid_user_1=current_user, uuid_user_2=req_user)

    elif RelationUserConnection.objects.all().filter(uuid_user_1=req_user, uuid_user_2=current_user).exists():
        relation_status = RelationUserConnection.objects.get(uuid_user_1=req_user, uuid_user_2=current_user)

    else:
        relation_status = 'None'

    # Get connections common between current user and the requested user page
    common_connects_set = []
    unique_connects = []

    for connect in connects:
        if connect not in common_connects_set:
            unique_connects.append(connect)
            common_connects_set.append(connect)

    #Select five random users in common and pass to view
    def randselect(commons):
        if current_user.id not in commons:
            pass
        else:
            commons.remove(current_user.id)
            commons.remove(req_user.id)
        commons_count = len(commons)
        if commons_count > 5:
            get_these_users = random.sample(commons, 5)

        else:
            get_these_users = commons

        return get_these_users

    common_connects_list = randselect(common_connects_set)

    # http://stackoverflow.com/questions/852414/how-to-dynamically-compose-an-or-query-filter-in-django
    connects_in_common = User.objects.filter(pk__in=common_connects_list)

    '''connect_users = []

    for connect in common_connects_set:
        append_this_obj = User.objects.values('first_name', 'last_name').all().filter(id__in=str(connect))
        connect_users.append(append_this_obj)'''

    context_dict_local = {'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme, 'relation_status': relation_status, 'common_connects': connects_in_common}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    return render(request, 'allonsy/user_main.html', context_dict, context_instance=RequestContext(request))


@login_required
def edit_user_url(request, username):

    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)
    context_dict_local = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme}
    # return render(request, 'allonsy/user.html', context_dict)

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    if current_user_acct == req_user_acct:

        return render(request, 'allonsy/forms/edituser.html', context_dict, context_instance=RequestContext(request))

    else:
        # Return a 'disabled account' error message
        return HttpResponse("Disabled")


@login_required
def resolve_org_url(request, orgname):
    #TODO: UPDATE WITH HELPER FUNCTIONS
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


@user_passes_test(allonsy_dev_check)
@login_required
def do_add_account(request):
    do_add_account_form = DoAddAccount(request.POST)
    current_user = request.user
    req_user = request.user

    context_dict = {'form': do_add_account_form, 'cur_user': current_user, 'req_user': req_user}

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
                return render_to_response('allonsy/forms/add-account.html', {'form': do_add_account_form})

    else:
            # Return a 'disabled account' error message
        return render(request, 'allonsy/forms/add-account.html', context_dict, context_instance=RequestContext(request))


@user_passes_test(access_admin_check)
@login_required
def do_add_organization(request):
    do_add_organization_form = DoAddOrganization(request.POST)
    current_user = request.user
    req_user = request.user

    context_dict = {'form': do_add_organization_form, 'cur_user': current_user, 'req_user': req_user}

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
                return render_to_response('allonsy/forms/organization.html', {'form': do_add_organization_form})

    else:
            # Return a 'disabled account' error message
        #return render_to_response('allonsy/forms/organization.html', {'form': do_add_organization_form})
        return render(request, 'allonsy/forms/add-org.html', context_dict, context_instance=RequestContext(request))


@user_passes_test(access_admin_check)
@login_required
def do_add_user(request):
    do_add_user_form = DoAddUser(request.POST)
    username = request.user
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    context_dict = {'form': do_add_user_form, 'cur_user': current_user, 'req_user': req_user}

    if request.method == 'POST':

        if do_add_user_form.is_valid():

            add_username = do_add_user_form.cleaned_data['username']
            add_password = do_add_user_form.cleaned_data['password']
            conf_password = do_add_user_form.cleaned_data['conf_password']
            add_email = do_add_user_form.cleaned_data['email']
            add_first_name = do_add_user_form.cleaned_data['first_name']
            add_last_name = do_add_user_form.cleaned_data['last_name']
            is_superuser = do_add_user_form.cleaned_data['is_superuser']
            is_staff = do_add_user_form.cleaned_data['is_staff']
            fk_val = req_user_acct

            if add_password == conf_password:

                new_user = User.objects.create_user(username=add_username,
                                                    password=add_password,
                                                    email=add_email,
                                                    )

                new_user.first_name = add_first_name
                new_user.last_name = add_last_name
                new_user.is_superuser = is_superuser
                new_user.is_staff = is_staff
                new_user.save()

                new_user_object = User.objects.get(username=add_username)

                new_user_extension = UserExtension.objects.create(uuid_account=fk_val,
                                                                  user=new_user_object)

                new_user_extension_fk = UserExtension.objects.get(user=new_user_object)

                new_user_profile = UserProfile.objects.create(user=new_user_object,
                                                              uuid_user=new_user_extension_fk)

                new_user_extension.save()
                new_user_profile.save()

                return HttpResponseRedirect('/user/'+str(add_username))

            else:
                return HttpResponse("Passwords don't match!")

        else:
                # Return a 'disabled account' error message
                #return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))
                return render(request, 'allonsy/forms/add-location.html', context_dict, context_instance=RequestContext(request))

    else:

        return render(request, 'allonsy/forms/add-user.html', context_dict, context_instance=RequestContext(request))


@user_passes_test(access_admin_check)
@login_required
def do_add_location(request):
    do_add_location_form = DoAddLocation(request.POST)
    current_user = request.user
    req_user = request.user

    context_dict = {'form': do_add_location_form, 'cur_user': current_user, 'req_user': req_user}

    if request.method == 'POST':
        fk_val = request.user.userextension.uuid_account

        if do_add_location_form.is_valid():
            location_InheritGeoFromParent = do_add_location_form.cleaned_data['location_InheritGeoFromParent']
            location_HasParent = do_add_location_form['location_HasParent']
            location_type = do_add_location_form.cleaned_data['location_type']
            location_SubLocIdent = do_add_location_form.cleaned_data['location_SubLocIdent']
            location_FullName = do_add_location_form.cleaned_data['location_FullName']
            location_ShortName = do_add_location_form.cleaned_data['location_ShortName']
            location_abbreviation = do_add_location_form.cleaned_data['location_abbreviation']
            location_country_id = do_add_location_form.cleaned_data['location_country_id']
            location_province_name = do_add_location_form.cleaned_data['location_province_name']
            location_city_name = do_add_location_form.cleaned_data['location_city_name']
            location_PostalCode = do_add_location_form.cleaned_data['location_PostalCode']
            location_street_number = do_add_location_form.cleaned_data['location_street_number']
            location_street_name = do_add_location_form.cleaned_data['location_street_name']
            location_ApartmentNumber = do_add_location_form.cleaned_data['location_ApartmentNumber']
            location_CountryCode = do_add_location_form.cleaned_data['location_CountryCode']
            location_phone_value = do_add_location_form.cleaned_data['location_phone_value']

            proto_form = Location.objects.create(
                uuid_account=fk_val,
                location_InheritGeoFromParent=location_InheritGeoFromParent,
                location_HasParent=location_HasParent,
                location_type=location_type,
                location_SubLocIdent=location_SubLocIdent,
                location_FullName=location_FullName,
                location_ShortName=location_ShortName,
                location_abbreviation=location_abbreviation,
                location_country_id=location_country_id,
                location_province_name=location_province_name,
                location_city_name=location_city_name,
                location_PostalCode=location_PostalCode,
                location_street_number=location_street_number,
                location_street_name=location_street_name,
                location_ApartmentNumber=location_ApartmentNumber,
                location_CountryCode=location_CountryCode,
                location_phone_value=location_phone_value,
            )

            proto_form.save()

            return render(request, 'allonsy/user.html')

        else:
                # Return a 'disabled account' error message
            return render(request, 'allonsy/forms/add-location.html', context_dict, context_instance=RequestContext(request))
            #return HttpResponseRedirect("Failed validation")

    else:
            # Return a 'disabled account' error message
        return render(request, 'allonsy/forms/add-location.html', context_dict, context_instance=RequestContext(request))


@user_passes_test(access_admin_check)
@login_required
def assoc_organization(request):
    orglist = Organization.objects.all().filter(uuid_account=request.user.userextension.uuid_account)
    return render(request, 'allonsy/forms/associate-org.html', {'orgs': orglist}, context_instance=RequestContext(request))


@user_passes_test(access_admin_check)
@login_required
def do_assoc_organization(request, username):
    #TODO: Handle exception when user attempts to assign same org as child. Should pop error modal and ask if sure user wishes to move the node. Modify node.parent to complete.
    do_assoc_organization_form = DoAssocOrganization(request.POST)
    orglist = Organization.objects.all().filter(uuid_account=request.user.userextension.uuid_account)
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
        #return render_to_response('allonsy/organization.html', {'form': do_assoc_organization_form})
        return render(request, 'allonsy/forms/associate-org.html', {'orgs': orglist}, context_instance=RequestContext(request))


@user_passes_test(access_admin_check)
@login_required
def assoc_organization_user(request):
    orglist = Organization.objects.all().filter(uuid_account=request.user.userextension.uuid_account)
    usrlist = UserExtension.objects.all().filter(uuid_account=request.user.userextension.uuid_account)
    return render(request, 'allonsy/associate-user.html', {'orgs': orglist, 'users': usrlist}, context_instance=RequestContext(request))


@user_passes_test(access_admin_check)
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
def do_get_user_alerts(request, username):

    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    new_user_interactions = UserInteractionTree.objects.all().filter(interaction_target=current_user, interaction_status='O')
    count_new_user_interactions = new_user_interactions.count
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    current_user_interactions = UserAlert.objects.all().filter(Q(interaction_target=current_user), Q(interaction_status='O') | Q(interaction_status='I'))

    context_dict_local = {'cur_user_interacts': current_user_interactions, 'orgs_primary': req_user_orgs_primary, 'count_new_user_interactions': count_new_user_interactions}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    return render(request, 'allonsy/user_interactions.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_get_user_interactions(request, username):

    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    new_user_interactions = UserInteractionTree.objects.all().filter(interaction_target=current_user, interaction_status='O')
    count_new_user_interactions = new_user_interactions.count
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    current_user_interactions = UserInteractionTree.objects.all().filter(Q(interaction_target=current_user), Q(interaction_status='O') | Q(interaction_status='I'))
    current_user_sent = UserInteractionTree.objects.all().filter(interaction_sender=current_user)

    context_dict_local = {'cur_user_interacts': current_user_interactions, 'cur_user_sent': current_user_sent, 'orgs_primary': req_user_orgs_primary, 'count_new_user_interactions': count_new_user_interactions}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    return render(request, 'allonsy/user_interactions.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_get_user_sent(request, username):
    current_user = User.objects.get(username=request.user)
    new_user_interactions = UserInteractionTree.objects.all().filter(interaction_target=current_user, interaction_status='O')
    count_new_user_interactions = new_user_interactions.count
    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    #current_user_interactions = UserInteraction.objects.all()
    current_user_sent = UserInteractionTree.objects.all().filter(Q(interaction_sender=current_user))

    context_dict = {'cur_user': current_user,  'req_user': req_user, 'req_userextension': req_userextension, 'cur_user_interacts': current_user_sent, 'orgs_primary': req_user_orgs_primary, 'count_new_user_interactions': count_new_user_interactions}

    return render(request, 'allonsy/user_interactions.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_user_connect(request, username):
    do_user_connect_form = DoUserConnect(request.POST)

    #Request context_helper for user object toolkit
    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    #Local context space. Don't forget to add to local context!


    #Add local context
    context_dict_local = {'orgs_primary': ''}
    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)
    interaction_subject_text = 'New connection request from ' + current_user.first_name + ' ' + current_user.last_name
    #interaction_direction_sent = 'S'
    #interaction_direction_received = 'R'
    interaction_status_sent = 'I'
    interaction_status_received = 'O'
    interaction_type = 'C'
    relation_status = 'P'

    if request.method == 'POST':
        if do_user_connect_form.is_valid():
            if RelationUserConnection.objects.filter(uuid_user_1=current_user, uuid_user_2=req_user).exists():
                return HttpResponse("Exists")

            elif RelationUserConnection.objects.filter(uuid_user_2=current_user, uuid_user_1=req_user).exists():
                return HttpResponse("Exists")

            else:

                proto_relation_uuid = uuid.uuid4()

                proto_interaction_sender = UserInteractionTree.objects.create(
                    #interaction_direction=interaction_direction_sent,
                    interaction_status=interaction_status_sent,
                    interaction_type=interaction_type,
                    interaction_subject=interaction_subject_text,
                    interaction_text=do_user_connect_form.cleaned_data['interaction_text']
                )

                proto_interaction_sender.save()
                # many to many only after create
                proto_interaction_sender.interaction_target.add(req_user)
                proto_interaction_sender.interaction_sender.add(current_user)

                proto_interaction_receiver = UserInteractionTree.objects.create(
                    #interaction_direction=interaction_direction_received,
                    interaction_status=interaction_status_received,
                    interaction_type=interaction_type,
                    interaction_subject=interaction_subject_text,
                    interaction_text=do_user_connect_form.cleaned_data['interaction_text']
                )

                proto_interaction_receiver.save()
                # many to many only after create
                proto_interaction_receiver.interaction_target.add(req_user)
                proto_interaction_receiver.interaction_sender.add(current_user)

                proto_relation_status = RelationUserConnection.objects.create(
                    uuid_relation=proto_relation_uuid,
                    relation_type=do_user_connect_form.cleaned_data['relation_type'],
                    relation_status=relation_status
                )

                proto_relation_status.save()
                proto_relation_status.uuid_user_1.add(current_user)
                proto_relation_status.uuid_user_2.add(req_user)

                proto_relation = RelationUserConnection.objects.get(uuid_relation=proto_relation_uuid)
                proto_interaction_sender.uuid_request.add(proto_relation)
                proto_interaction_receiver.uuid_request.add(proto_relation)

                return redirect('resolve_user_url', req_user.username)

        else:
                # TODO: CHANGE
            return render(request, 'allonsy/user_main.html', context_dict, context_instance=RequestContext(request))
            #return HttpResponseRedirect("Failed validation")

    else:
            # TODO: CHANGE
        return render(request, 'allonsy/user.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_update_connect_status(request, username, status, cstatus, uuidmsg):

    #Request context_helper for user object toolkit
    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    #Local context space. Don't forget to add to local context!


    #Add local context
    this_user_interaction = UserInteractionTree.objects.get(uuid_interaction=uuidmsg)
    this_user_crequest_list = UserInteractionTree.objects.filter(uuid_interaction=uuidmsg).values_list('uuid_request', flat=True)
    this_user_crequest = this_user_crequest_list[0]

    # May cause problems and need to be converted to UUID see here:
    # http://stackoverflow.com/questions/15859156/python-how-to-convert-a-valid-uuid-from-string-to-uuid
    # this_connection_request = this_user_interaction.uuid_request.values('id').all()
    # this_connection = RelationUserConnection.objects.get(id=this_connection_request)

    this_connection_update = RelationUserConnection.objects.get(id=this_user_crequest)

    this_interaction_status_raw = str(status)
    this_crequest_cstatus_raw = str(cstatus)
    # Get only the first character to avoid bad inputs
    this_interaction_status_new = this_interaction_status_raw[0]
    this_crequest_cstatus_new = this_crequest_cstatus_raw[0]

    context_dict_local = {'orgs_primary': ''}
    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    if this_crequest_cstatus_new == 'A':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()
        this_connection_update.relation_status = this_crequest_cstatus_new

        this_user_interaction.save()
        this_connection_update.save()

        return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

    elif this_interaction_status_new == 'P':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

    elif this_interaction_status_new == 'R':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

    elif this_interaction_status_new == 'D':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

    else:
        return HttpResponse('Fail 2')
        #return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))


@login_required
def do_send_reply_message(request, username, uuidmsg):
    do_send_reply_message_form = DoSendReplyMessage(request.POST)

    current_user = User.objects.get(username=request.user)
    new_user_interactions = UserInteractionTree.objects.all().filter(interaction_target=current_user, interaction_status='O')
    count_new_user_interactions = new_user_interactions.count
    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    this_user_interaction = UserInteractionTree.objects.get(uuid_interaction=uuidmsg)
    this_user_interaction_sender = this_user_interaction.interaction_sender.values('id').all()

    context_dict = {'cur_user': current_user,
                    'req_user': req_user,
                    'req_userextension': req_userextension,
                    'cur_user_interacts': this_user_interaction,
                    'orgs_primary': req_user_orgs_primary,
                    'count_new_user_interactions': count_new_user_interactions}

    if request.method == 'POST':
        if do_send_reply_message_form.is_valid():
            interaction_subject = do_send_reply_message_form.cleaned_data['interaction_subject']
            interaction_text = do_send_reply_message_form.cleaned_data['interaction_text']
            interaction_sender = current_user
            interaction_type = 'M'
            interaction_status = 'O'
            interaction_target = User.objects.get(id=this_user_interaction_sender)
            #interaction_direction_target = 'R'
            #interaction_direction_sender = 'S'
            uuid_previous_msg = this_user_interaction

            this_user_interaction.interaction_status = 'I'
            this_user_interaction.save()

            #Create first of two ledger records

            do_create_reply_message_1 = UserInteractionTree.objects.create(interaction_subject=interaction_subject,
                                                                           interaction_text=interaction_text,
                                                                           interaction_type=interaction_type,
                                                                           interaction_status=interaction_status,
                                                                           #interaction_direction=interaction_direction_target,
                                                                           parent=uuid_previous_msg,
                                                                           )

            #many-to-many only after object created
            do_create_reply_message_1.save()
            do_create_reply_message_1.interaction_target.add(interaction_target)
            do_create_reply_message_1.interaction_sender.add(current_user)

            #Create second of two ledger records

            '''do_create_reply_message_2 = UserInteraction.objects.create(interaction_subject=interaction_subject,
                                                                       interaction_text=interaction_text,
                                                                       interaction_type=interaction_type,
                                                                       interaction_status=interaction_status,
                                                                       interaction_direction=interaction_direction_sender)

            #many-to-many only after object created
            do_create_reply_message_2.save()
            do_create_reply_message_2.interaction_target.add(interaction_target)
            do_create_reply_message_2.interaction_sender.add(current_user)'''

            return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

        else:
            return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

    else:
        return HttpResponse('Fail 3')


@login_required
def do_send_message(request, username):
    do_send_message_form = DoSendMessage(request.POST)
    current_user = User.objects.get(username=request.user)
    req_user = User.objects.get(username=username)
    interaction_sender = current_user
    interaction_target = req_user
    interaction_type = 'M'
    interaction_status = 'O'

    if request.method == 'POST':
        if do_send_message_form.is_valid():

            interaction_subject = do_send_message_form.cleaned_data['interaction_subject']
            interaction_text = do_send_message_form.cleaned_data['interaction_text']

            do_create_reply_message_1 = UserInteractionTree.objects.create(interaction_subject=interaction_subject,
                                                                           interaction_text=interaction_text,
                                                                           interaction_type=interaction_type,
                                                                           interaction_status=interaction_status,
                                                                           )

            #many-to-many only after object created
            do_create_reply_message_1.save()
            do_create_reply_message_1.interaction_target.add(interaction_target)
            do_create_reply_message_1.interaction_sender.add(interaction_sender)

            return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

        else:
            return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

    else:
        return HttpResponse('Fail 3')


@login_required
def do_update_msg_status(request, username, status, uuidmsg):

    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    this_user_interaction = UserInteractionTree.objects.get(uuid_interaction=uuidmsg)
    this_interaction_status_raw = str(status)
    # Get only the first character to avoid bad inputs
    this_interaction_status_new = this_interaction_status_raw[0]

    if this_interaction_status_new == 'I':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

    elif this_interaction_status_new == 'O':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

    elif this_interaction_status_new == 'X':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

    elif this_interaction_status_new == 'F':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

    else:
        return HttpResponse('Fail 2')
        #return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))


@login_required
def do_update_alert_status(request, username, status, uuidmsg):

    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    this_user_interaction = UserAlert.objects.get(uuid_alert=uuidmsg)
    this_interaction_status_raw = str(status)
    # Get only the first character to avoid bad inputs
    this_interaction_status_new = this_interaction_status_raw[0]

    if this_interaction_status_new == 'I':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_alerts', kwargs={'username': username}))

    elif this_interaction_status_new == 'O':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_alerts', kwargs={'username': username}))

    elif this_interaction_status_new == 'X':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_alerts', kwargs={'username': username}))

    elif this_interaction_status_new == 'F':
        this_user_interaction.interaction_status = this_interaction_status_new
        this_user_interaction.save()

        return HttpResponseRedirect(reverse('do_get_user_alerts', kwargs={'username': username}))

    else:
        return HttpResponse('Fail 2')
        #return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))


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
        return render(request, 'allonsy/forms/user_edituser.html', context_dict, context_instance=RequestContext(request))

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
        return render(request, 'allonsy/forms/user_editusercontacts.html', context_dict, context_instance=RequestContext(request))


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

            return render(request, 'allonsy/forms/user_editemergencycontacts.html', context_dict, context_instance=RequestContext(request))

    else:
            # Return a 'disabled account' error message

        return render(request, 'allonsy/forms/user_editemergencycontacts.html', context_dict, context_instance=RequestContext(request))


def roles_dashboard(request, username):

    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    context_dict_local = {'orgs_primary': req_user_orgs_primary}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    return render(request, 'allonsy/roles_dashboard.html', context_dict, context_instance=RequestContext(request))


def roles_oncall(request, username):
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

    context_dict = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary,}

    return render(request, 'allonsy/roles_oncall.html', context_dict, context_instance=RequestContext(request))


def roles_onduty(request, username):
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

    context_dict = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary,}

    return render(request, 'allonsy/roles_onduty.html', context_dict, context_instance=RequestContext(request))


def wf_set_add_or_edit(request):

    wf_set_add_or_edit_form = DoAddEditWFSet(request.POST)

    username = request.user
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {'form': wf_set_add_or_edit_form}
    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    if request.method == 'POST':
        if wf_set_add_or_edit_form.is_valid():
            uuid_wf_set = uuid.uuid4()
            wf_set_name = wf_set_add_or_edit_form.cleaned_data['wf_set_name']
            wf_set_is_type = wf_set_add_or_edit_form.cleaned_data['wf_set_is_type']
            wf_set_is_default_parent_for_type = wf_set_add_or_edit_form.cleaned_data['wf_set_is_default_parent_for_type']
            wf_set_has_child = wf_set_add_or_edit_form.cleaned_data['wf_set_has_child']
            wf_set_is_active = wf_set_add_or_edit_form.cleaned_data['wf_set_is_active']

            do_create_wf_object = WorkflowSet.objects.create(uuid_wf_set=uuid_wf_set,
                                                             wf_set_name=wf_set_name,
                                                             wf_set_is_type=wf_set_is_type,
                                                             wf_set_is_default_parent_for_type=wf_set_is_default_parent_for_type,
                                                             wf_set_has_child=wf_set_has_child,
                                                             wf_set_is_active=wf_set_is_active)

            do_create_wf_object.save()

            if wf_set_has_child is True:
                return HttpResponseRedirect(reverse('wf_set_add_children', kwargs={'uuidwfparent': uuid_wf_set}))
            else:
                return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

        else:

            return render(request, 'allonsy/forms/wf_create.html', context_dict, context_instance=RequestContext(request))
            #return render_to_response('allonsy/forms/wf_create.html', {'form': wf_set_add_or_edit_form})

    else:
            # Return a 'disabled account' error message

        return render(request, 'allonsy/forms/wf_create.html', context_dict, context_instance=RequestContext(request))


def wf_set_add_children(request, uuidwfparent):
    wf_set_add_or_edit_form = DoAddEditWFChild(request.POST)

    username = request.user
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {'form': wf_set_add_or_edit_form}
    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    parent_wf_object = WorkflowSet.objects.get(uuid_wf_set=uuidwfparent)

    if request.method == 'POST':
        if wf_set_add_or_edit_form.is_valid():
            uuid_wf_set = uuid.uuid4()
            uuid_wf_rel = uuid.uuid4()
            wf_set_name = wf_set_add_or_edit_form.cleaned_data['wf_set_name']
            wf_set_is_type = parent_wf_object.wf_set_is_type
            wf_set_is_default_parent_for_type = False
            wf_set_has_child = False
            wf_set_is_active = wf_set_add_or_edit_form.cleaned_data['wf_set_is_active']
            wf_disp_order = wf_set_add_or_edit_form.cleaned_data['wf_disp_order']

            do_create_wf_object = WorkflowSet.objects.create(uuid_wf_set=uuid_wf_set,
                                                             wf_set_name=wf_set_name,
                                                             wf_set_is_type=wf_set_is_type,
                                                             wf_set_is_default_parent_for_type=wf_set_is_default_parent_for_type,
                                                             wf_set_has_child=wf_set_has_child,
                                                             wf_set_is_active=wf_set_is_active)

            proto_do_create_wf_rel_object = RelationWorkflow.objects.create(uuid_relation=uuid_wf_rel,
                                                                            wf_disp_order=wf_disp_order)

            do_create_wf_object.save()
            proto_do_create_wf_rel_object.save()

            child_wf_object = WorkflowSet.objects.get(uuid_wf_set=uuid_wf_set)
            # many to many only after create
            do_create_wf_rel_object = proto_do_create_wf_rel_object
            do_create_wf_rel_object.wf_parent.add(parent_wf_object)
            do_create_wf_rel_object.wf_child.add(child_wf_object)

            do_create_wf_rel_object.save()

            return HttpResponseRedirect(reverse('wf_set_add_items', kwargs={'uuidwfparent': uuid_wf_set}))

        else:

            return render(request, 'allonsy/forms/wf_child_create.html', context_dict, context_instance=RequestContext(request))
            #return render_to_response('allonsy/forms/wf_create.html', {'form': wf_set_add_or_edit_form})

    else:
            # Return a 'disabled account' error message

        return render(request, 'allonsy/forms/wf_child_create.html', context_dict, context_instance=RequestContext(request))


def wf_set_add_items(request, uuidwfparent):
    wf_items_add_or_edit_form = DoAddEditWFItem(request.POST)

    username = request.user
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {'form': wf_items_add_or_edit_form}
    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    parent_wf_object = WorkflowSet.objects.get(uuid_wf_set=uuidwfparent)

    if request.method == 'POST':
        if wf_items_add_or_edit_form.is_valid():
            uuid_wf_item = uuid.uuid4()
            wf_item_is_active = wf_items_add_or_edit_form.cleaned_data['wf_item_is_active']
            wf_item_name = wf_items_add_or_edit_form.cleaned_data['wf_item_name']
            wf_item_text = wf_items_add_or_edit_form.cleaned_data['wf_item_text']
            wf_item_disp_order = wf_items_add_or_edit_form.cleaned_data['wf_item_disp_order']

            proto_do_create_wf_object = WorkflowItem.objects.create(uuid_wf_item=uuid_wf_item,
                                                                   wf_item_is_active=wf_item_is_active,
                                                                   wf_item_name=wf_item_name,
                                                                   wf_item_text=wf_item_text,
                                                                   wf_item_disp_order=wf_item_disp_order)

            proto_do_create_wf_object.save()
            # many to many only after create
            do_create_wf_object = proto_do_create_wf_object
            do_create_wf_object.wf_item_parent_wfset.add(parent_wf_object)

            do_create_wf_object.save()

            return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username}))

        else:

            return render(request, 'allonsy/forms/wf_item_create.html', context_dict, context_instance=RequestContext(request))
            #return render_to_response('allonsy/forms/wf_create.html', {'form': wf_set_add_or_edit_form})

    else:
            # Return a 'disabled account' error message

        return render(request, 'allonsy/forms/wf_item_create.html', context_dict, context_instance=RequestContext(request))


def app(request):
    return render(request, 'allonsy/app.html')
