import time, uuid, random, copy, collections
from uuid import UUID
from itertools import chain
from datetime import date

from django.shortcuts import render, render_to_response, RequestContext, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q

from mptt.exceptions import *
from django_ajax.decorators import ajax

from allonsy_main.forms import DoAddAccount, DoAddOrganization, DoAddLocation, DoAddUser, DoAssocOrganization, DoAssocOrganizationUser, DoEditUserProfile, DoEditUserInfoContact, DoEditUserEmergencyContact, DoUserConnect, DoSendReplyMessage, DoSendMessage, DoAddEditWFSet, DoAddEditWFChild, DoAddEditWFItem, DoAddEditWFTreeNode, DoGetWFTreeForAddItem, DoAddWFTreeItem, DoDeleteWFTreeItem, DoGetWFInstance, DoEditWFInstanceMeta, DoAddEpoch, DoGetLocForm, DoGetUserSelectForm
from allonsy_main.models import UserInteractionThread, UserInteractionPayload, UserInteractionRouting, UserInteractionReadState, UserExtension, User, UserProfile, Organization, RelationOrganizationUser, UserInteractionTree, UserAlert, Location, RelationUserConnection, WorkflowSet, RelationWorkflow, WorkflowItem, RelationWorkflow, WorkflowItem, WorkflowDocumentItem, WorkflowDocumentMaster, WorkflowTree, Epoch
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

    # Get defaults for workflows. Case insensitive
    # TODO: Document the icontains descriptors for new account setup
    wf_oncall = str(WorkflowTree.objects.values_list('uuid_wf_item', flat=True).get(wf_item_name__icontains='RA Duty', level=2))

    context_helper = {'current_user_obj': current_user_obj,
                      'cur_user': current_user,
                      'current_userextension': current_userextension,
                      'current_user_acct': current_user_acct,
                      'req_user': req_user,
                      'req_userextension': req_userextension,
                      'req_user_acct': req_user_acct,
                      'req_user_uuid': req_user_uuid,
                      'wf_oncall': wf_oncall
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


# 1e406955-5f6a-4992-b44f-13a9b7d0d828
def get_dyn_items(request, uuidparentnode):
    wf_parent = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)
    wf_columns = wf_parent.get_children()
    dyn_items_list = []

    for column in wf_columns:
        dyn_items_list_loc = column.get_children()
        dyn_items_list.extend(dyn_items_list_loc)

    return dyn_items_list


def get_dyn_columns(request, uuidparentnode):
    wf_parent = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)
    wf_columns = wf_parent.get_children()
    dyn_columns_list = wf_columns

    return dyn_columns_list


def get_user_orgs(req_user, req_user_uuid):
    user_orgs_list = RelationOrganizationUser.objects.filter(Q(uuid_user=req_user_uuid) & Q(date_expires__gt=date.today()))

    return user_orgs_list


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
def app(request):
    return render(request, 'allonsy/app.html')


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
    #TODO: Sort org objects so the highest level are on top. Opens opportunity to sort by user-defined options
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    req_orgs_affil = Organization.objects.filter(org_type_special='A').order_by('level')
    req_user_orgs_affil_list = RelationOrganizationUser.objects.values_list('uuid_org', flat=True).filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    org_affil_list = []

    for affil in req_user_orgs_affil_list:
        uuid_org = affil
        get_org = Organization.objects.get(uuid_org=uuid_org)
        org_affil_list.append(get_org)

    req_orgs_interest = Organization.objects.filter(org_type_special='I')
    req_user_orgs_interest_list = RelationOrganizationUser.objects.values_list('uuid_org', flat=True).filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_interest)
    org_interest_list = []

    for interest in req_user_orgs_interest_list:
        uuid_org = interest
        get_org = Organization.objects.get(uuid_org=uuid_org)
        org_interest_list.append(get_org)

    req_orgs_achieve = Organization.objects.filter(org_type_special='V')
    req_user_orgs_achieve_list = RelationOrganizationUser.objects.values_list('uuid_org', flat=True).filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_achieve)
    org_achieve_list = []

    for achieve in req_user_orgs_achieve_list:
        uuid_org = achieve
        get_org = Organization.objects.get(uuid_org=uuid_org)
        org_achieve_list.append(get_org)

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

    context_dict_local = {'orgs_affil': org_affil_list, 'orgs_interest': org_interest_list, 'orgs_achieve': org_achieve_list, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme, 'relation_status': relation_status, 'common_connects': connects_in_common}

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
def org_live(request):
    username = request.user
    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict = context_helper.copy()

    user_orgs_list = get_user_orgs(req_user, req_user_uuid)

    return ()


@login_required
def resolve_org_url(request, orgname):
    username = request.user
    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict = context_helper.copy()
    user_orgs_list = get_user_orgs(req_user, req_user_uuid)
    current_user_auth = 'True'

    #TODO: Add auth that user is allowed to see this group and/or interact

    try:
        check_this = UUID(orgname, version=4)
        get_short_name = Organization.objects.values_list('org_ShortName', flat=True).get(pk=check_this)
        org_short_name = get_short_name.replace(' ', '-')

        return redirect('resolve_org_url', org_short_name)

    except ValueError:
        org_short_name = orgname.replace('-', ' ')

        get_org_obj = Organization.objects.get(org_ShortName=org_short_name)
        context_dict_local = {'current_user': current_user, 'current_user_auth': current_user_auth, 'org_obj': get_org_obj, 'org_short_name': org_short_name, 'orgs_list':user_orgs_list}
        context_dict.update(context_dict_local)

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

    # Creates list of potential parent organizations and passes to view
    org_parent_list = Organization.objects.all()

    context_dict = {'form': do_add_organization_form, 'cur_user': current_user, 'req_user': req_user, 'org_parent_list': org_parent_list}

    if request.method == 'POST':

        if do_add_organization_form.is_valid():
            org_parent = do_add_organization_form.cleaned_data['org_parent']
            org_FullName = do_add_organization_form.cleaned_data['org_FullName']
            org_ShortName = do_add_organization_form.cleaned_data['org_ShortName']
            org_abbreviation = do_add_organization_form.cleaned_data['org_abbreviation']
            org_type = do_add_organization_form.cleaned_data['org_type']
            org_type_special = do_add_organization_form.cleaned_data['org_type_special']

            get_org_parent = Organization.objects.get(uuid_org=org_parent)

            proto_org = Organization.objects.create(parent=get_org_parent,
                                                    org_FullName=org_FullName,
                                                    org_ShortName=org_ShortName,
                                                    org_abbreviation=org_abbreviation,
                                                    org_type=org_type,
                                                    org_type_special=org_type_special,
                                                    )

            proto_org.save()

            return redirect('user_admin')
            # return render(request, 'allonsy/user.html')

        else:
                # Return a 'disabled account' error message
                return render_to_response('allonsy/forms/organization.html', {'form': do_add_organization_form})

    else:
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

    location_parent_list = Location.objects.all().order_by('level', 'location_ShortName')

    context_dict = {'form': do_add_location_form, 'cur_user': current_user, 'req_user': req_user, 'location_parent_list': location_parent_list}

    if request.method == 'POST':

        if do_add_location_form.is_valid():
            location_InheritGeoFromParent = do_add_location_form.cleaned_data['location_InheritGeoFromParent']
            location_parent = do_add_location_form.cleaned_data['location_parent']
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
                location_InheritGeoFromParent=location_InheritGeoFromParent,
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

            proto_form.parent = Location.objects.get(uuid_location=location_parent)

            proto_form.save()

            return render(request, 'allonsy/user.html')

        else:
                # Return a 'disabled account' error message
            return render(request, 'allonsy/forms/add-location.html', context_dict, context_instance=RequestContext(request))
            #return HttpResponseRedirect("Failed validation")

    else:
            # Return a 'disabled account' error message
        return render(request, 'allonsy/forms/add-location.html', context_dict, context_instance=RequestContext(request))


'''@user_passes_test(access_admin_check)
@login_required
def assoc_organization(request):
    orglist = Organization.objects.all().filter(uuid_account=request.user.userextension.uuid_account)
    return render(request, 'allonsy/forms/associate-org.html', {'orgs': orglist}, context_instance=RequestContext(request))'''


@user_passes_test(access_admin_check)
@login_required
def do_assoc_organization(request, username):
    # TODO: REWRITE now that the tree is located in the org table
    # TODO: Handle exception when user attempts to assign same org as child. Should pop error modal and ask if sure user wishes to move the node. Modify node.parent to complete.
    do_assoc_organization_form = DoAssocOrganization(request.POST)
    orglist_parent = Organization.objects.all()
    orglist_child = Organization.objects.exclude(org_type='A')
    if request.method == 'POST':
        if do_assoc_organization_form.is_valid():
            parent = do_assoc_organization_form.cleaned_data['parent']
            child = do_assoc_organization_form.cleaned_data['child']

            try:
                org_parent = Organization.objects.get(uuid_org=parent)
                org_child = Organization.objects.get(uuid_org=child)

                org_child.parent = org_parent

                org_child.save()

                return redirect('user_admin')

            except InvalidMove:
                return HttpResponse("Error, cannot be same")

        else:
            # Return a 'disabled account' error message
            return render_to_response('allonsy/organization.html', {'form': do_assoc_organization_form})

    else:
            # Return a 'disabled account' error message
        #return render_to_response('allonsy/organization.html', {'form': do_assoc_organization_form})
        return render(request, 'allonsy/forms/associate-org.html', {'orgs_parent': orglist_parent, 'orgs_child': orglist_child}, context_instance=RequestContext(request))


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

    orglist = Organization.objects.all().filter().all()
    usrlist = UserExtension.objects.all().filter().all()

    context_dict = {'orglist': orglist, 'usrlist': usrlist}

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

                return redirect('resolve_user_url', assoc_usr_name)

        else:
            # Return a 'disabled account' error message
            return render_to_response('allonsy/associate-user.html', {'form': do_assoc_organization_user_form})
            # return HttpResponse('Fail 1')

    else:

        return render(request, 'allonsy/associate-user.html', context_dict, context_instance=RequestContext(request))


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
def get_user_interactions(request, username):

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    new_user_interactions_lookup = UserInteractionReadState.objects.all().filter(uuid_participant=current_user, read_state='O')
    count_new_user_interactions = new_user_interactions_lookup.count

    #TODO: Add a "new" interactions item for first-time views and an "unread" for interactions that have no yet been clicked
    #TODO: New and unread interactions should both appear bold
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    current_user_interaction_states = UserInteractionReadState.objects.all().filter(Q(uuid_participant=current_user), Q(read_state='O') | Q(read_state='I')).order_by('date_added')
    current_state_dict = {}

    for state in current_user_interaction_states:
        uuid_payload = state.uuid_payload.values('uuid_payload')
        get_payload = UserInteractionPayload.objects.filter(uuid_payload=uuid_payload)
        subject = get_payload.values_list('payload_subject', flat=True)
        text = get_payload.values_list('payload_text', flat=True)
        uuid_thread = get_payload.uuid_thread
        get_thread_value = UserInteractionThread.objects.filter(uuid_thread=uuid_thread).values_list('uuid_thread', flat=True)
        thread_dict = {}
        thread_dict[get_thread_value] = {'subject': subject, 'text': text}
        current_state_dict.update(thread_dict)

    context_dict_local = {'orgs_primary': req_user_orgs_primary, 'count_new_user_interactions': count_new_user_interactions}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)
    context_dict['cur_user_interactions'] = current_state_dict

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
def user_connect(request, username):
    do_user_connect_form = DoUserConnect(request.POST)

    #Request context_helper for user object toolkit
    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    #Local context space. Don't forget to add to local context!

    #Add local context
    #TODO: Check if the line below is necessary
    context_dict_local = {'orgs_primary': ''}
    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)
    interaction_type = 'C'
    interaction_name = 'New connection request from ' + current_user.first_name + ' ' + current_user.last_name
    payload_subject_text = interaction_name
    readstate = 'O'
    relation_status = 'P'
    interaction_sender = current_user
    target_participant = req_user

    if request.method == 'POST':
        if do_user_connect_form.is_valid():
            if RelationUserConnection.objects.filter(uuid_user_1=current_user, uuid_user_2=req_user).exists():
                return HttpResponse("Exists")

            elif RelationUserConnection.objects.filter(uuid_user_2=current_user, uuid_user_1=req_user).exists():
                return HttpResponse("Exists")

            else:

                payload_text = do_user_connect_form.cleaned_data['interaction_text']

                interaction_uuid = uuid.uuid4()
                payload_uuid = uuid.uuid4()
                routing_uuid = uuid.uuid4()
                readstate_uuid = uuid.uuid4()
                readstate_uuid = uuid.uuid4()
                relation_uuid = uuid.uuid4()

                interaction_thread = UserInteractionThread.objects.create(
                    uuid_thread=interaction_uuid,
                    interaction_type=interaction_type,
                    interaction_name=interaction_name
                )

                interaction_thread.save()

                new_thread = UserInteractionThread.objects.get(uuid_thread=interaction_uuid)

                interaction_payload = UserInteractionPayload.objects.create(
                    uuid_payload=payload_uuid,
                    payload_subject=payload_subject_text,
                    payload_text=payload_text
                )

                interaction_thread.save()
                # many to many only after create
                interaction_payload.uuid_thread.add(new_thread)
                interaction_payload.uuid_sender.add(interaction_sender)

                new_payload = UserInteractionPayload.objects.get(uuid_payload=payload_uuid)

                interaction_routing = UserInteractionRouting.objects.create(
                    uuid_routing=routing_uuid,
                )

                interaction_routing.save()
                # many to many only after create
                interaction_routing.uuid_thread.add(new_thread)
                interaction_routing.uuid_participant.add(target_participant)

                interaction_readstate = UserInteractionReadState.objects.create(
                    uuid_readstate=readstate_uuid,
                    read_state=readstate
                )

                interaction_readstate.save()
                # many to many only after create
                interaction_readstate.uuid_payload.add(new_payload)
                interaction_readstate.uuid_participant.add(target_participant)

                relation_status = RelationUserConnection.objects.create(
                    uuid_relation=relation_uuid,
                    relation_type=do_user_connect_form.cleaned_data['relation_type'],
                    relation_status=relation_status
                )

                relation_status.save()
                relation_status.uuid_user_1.add(current_user)
                relation_status.uuid_user_2.add(req_user)

                # proto_relation = RelationUserConnection.objects.get(uuid_relation=proto_relation_uuid)
                # proto_interaction_sender.uuid_request.add(proto_relation)
                # proto_interaction_receiver.uuid_request.add(proto_relation)

                return redirect('resolve_user_url', req_user.username)

        else:
                # TODO: CHANGE
            return render(request, 'allonsy/user_main.html', context_dict, context_instance=RequestContext(request))
            #return HttpResponseRedirect("Failed validation")

    else:
            # TODO: CHANGE
        return render(request, 'allonsy/user.html', context_dict, context_instance=RequestContext(request))


'''@login_required
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
        return render(request, 'allonsy/user.html', context_dict, context_instance=RequestContext(request))'''


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
    # TODO: Approvals should be selected by individual. So my RAs should send reports to me directly.
    # TODO: As a workaround for the above, send only reports without an "approval by" in the meta. Need to add this field to wf_meta

    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)

    wf_review = WorkflowTree.objects.order_by('date_added').filter(Q(wf_item_status='R'), wf_item_owner=current_user, wf_item_proto_category='DUTY', level=4)
    wf_pending = WorkflowTree.objects.order_by('date_added').filter(Q(wf_item_status='C') | Q(wf_item_status='I') | Q(wf_item_status='R'), wf_item_owner=current_user, wf_item_proto_category='DUTY', level=4)
    wf_submitted = WorkflowTree.objects.order_by('date_added').filter(Q(wf_item_status='S') | Q(wf_item_status='A'), wf_item_owner=current_user, wf_item_proto_category='DUTY', level=4)
    wf_complete = WorkflowTree.objects.order_by('date_added').filter(Q(wf_item_status='O'), wf_item_owner=current_user, wf_item_proto_category='DUTY', level=4)

    if current_userextension.user_checkin_oncall is True:
        wf_approve = WorkflowTree.objects.order_by('date_added').filter(Q(wf_item_status='S'), wf_item_proto_category='DUTY', level=4)

    else:
        wf_approve = ''

    context_dict_local = {'orgs_primary': req_user_orgs_primary, 'current_userextension': current_userextension, 'wf_approve': wf_approve, 'wf_pending': wf_pending, 'wf_submitted': wf_submitted, 'wf_complete': wf_complete, 'wf_review': wf_review}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    return render(request, 'allonsy/roles_dashboard.html', context_dict, context_instance=RequestContext(request))


def roles_oncall(request, username):

    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)

    context_dict_local = {'orgs_primary': req_user_orgs_primary}
    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    return render(request, 'allonsy/roles_oncall.html', context_dict, context_instance=RequestContext(request))


def roles_onduty(request, username):

    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)

    wf_pending = WorkflowTree.objects.order_by('date_added').filter(Q(wf_item_status='C') | Q(wf_item_status='I') | Q(wf_item_status='R'), wf_item_owner=current_user, wf_item_proto_category='DUTY', level=4)
    wf_submitted = WorkflowTree.objects.order_by('date_added').filter(Q(wf_item_status='S') | Q(wf_item_status='A'), wf_item_owner=current_user, wf_item_proto_category='DUTY', level=4)
    wf_complete = WorkflowTree.objects.order_by('date_added').filter(Q(wf_item_status='O'), wf_item_owner=current_user, wf_item_proto_category='DUTY', level=4)

    context_dict_local = {'orgs_primary': req_user_orgs_primary, 'wf_pending': wf_pending, 'wf_submitted': wf_submitted, 'wf_complete': wf_complete}
    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

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


def roles_rpt_create_new(request, username, rpttype):
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    item_dict = {}
    context_dict_local = {}
    context_dict = context_helper.copy()
    #update context dict at end of function

    report_type = rpttype
    report_parent = WorkflowSet.objects.get(wf_set_is_type=report_type, wf_set_is_default_parent_for_type=True)
    report_parent_uuid = report_parent.uuid_wf_set

    if report_parent.wf_set_has_child is True:
        # returns a flat list of WorkflowSet PKs
        report_children = RelationWorkflow.objects.filter(wf_parent__uuid_wf_set=report_parent_uuid, wf_child__wf_set_is_active=True)
        report_children_list = report_children.values_list('wf_child', flat=True).order_by('wf_disp_order')

        for child in report_children_list:
            get_child = WorkflowSet.objects.get(pk=child)
            set_display_order = report_children.get(wf_child__pk=child).wf_disp_order
            context_dict_local['set'+set_display_order] = get_child

            get_child_items = WorkflowItem.objects.filter(wf_item_parent_wfset=get_child, wf_item_is_active=True)
            context_dict_local['set'+set_display_order+'_items'] = get_child_items

            # get_child_items = WorkflowItem.objects.filter(wf_item_parent_wfset=get_child, wf_item_is_active=True)
            # get_child_items_list = get_child_items.values_list('pk', flat=True).order_by('wf_item_disp_order')

            #for item in get_child_items_list:
                #get_item = WorkflowItem.objects.filter(pk=item)
                #item_display_order = get_child_items.get(pk=item).wf_item_disp_order
                #item_dict['items'] = get_item
                #context_dict_local['item'+set_display_order + '_' + item_display_order] = get_item

    else:
        get_child_items = WorkflowItem.objects.filter(wf_item_parent_wfset=report_parent, wf_item_is_active=True).order_by('wf_item_disp_order')
        context_dict_local['set1'] = get_child_items

    context_dict.update(context_dict_local)

    return render(request, 'allonsy/roles_onduty.html', context_dict, context_instance=RequestContext(request))


def wf_tree_node_add_or_edit(request):

    wf_tree_node_add_or_edit_form = DoAddEditWFTreeNode(request.POST)

    username = request.user
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {}
    add_this_list = []
    context_dict = context_helper.copy()

    wf_node_pk = WorkflowTree.objects.all().values_list('pk', flat=True)[:1]
    wf_root_node = WorkflowTree.objects.get(pk=wf_node_pk).get_root()
    wf_distant_parent_list = wf_root_node.get_children()

    for item in wf_distant_parent_list:
        add_this = item.get_children().values_list('wf_item_name', flat=True).order_by('wf_item_name')
        add_this_list.extend(add_this)

    context_dict_local.update({'wf_parent_list': add_this_list})

    context_dict.update(context_dict_local)

    if request.method == 'POST':
        if wf_tree_node_add_or_edit_form.is_valid():

            wf_item_name = wf_tree_node_add_or_edit_form.cleaned_data['wf_item_name']
            wf_item_text = wf_tree_node_add_or_edit_form.cleaned_data['wf_item_text']
            wf_item_is_default = wf_tree_node_add_or_edit_form.cleaned_data['wf_item_is_default']
            wf_item_is_active = wf_tree_node_add_or_edit_form.cleaned_data['wf_item_is_active']
            wf_item_is_proto = True

            wf_doc_parent_selection = wf_tree_node_add_or_edit_form.cleaned_data['proto_wf_doc_type']
            wf_doc_parent_node = WorkflowTree.objects.get(wf_item_name=wf_doc_parent_selection).get_children()
            wf_doc_parent_proto = wf_doc_parent_node.get(wf_item_is_proto=True)

            try:
                do_create_wf_object = WorkflowTree.objects.create(parent=wf_doc_parent_proto,
                                                                  uuid_wf_item=uuid.uuid4(),
                                                                  wf_item_name=wf_item_name,
                                                                  wf_item_text=wf_item_text,
                                                                  wf_item_is_default=wf_item_is_default,
                                                                  wf_item_is_proto=wf_item_is_proto,
                                                                  wf_item_is_active=wf_item_is_active,)
                do_create_wf_object.save()

                do_create_wf_object.wf_item_owner.add(current_user_obj)

            except IntegrityError:

                return HttpResponse('Name already exists!')

            return HttpResponse('Done!')

        else:

            context_dict_form_errors = {'form': wf_tree_node_add_or_edit}
            context_dict_local.update(context_dict_form_errors)
            context_dict.update(context_dict_local)

            return render(request, 'allonsy/forms/wf_tree_create.html', context_dict, context_instance=RequestContext(request))
            #return render_to_response('allonsy/forms/wf_create.html', {'form': wf_set_add_or_edit_form})

    else:

        return render(request, 'allonsy/forms/wf_tree_create.html', context_dict, context_instance=RequestContext(request))


def get_tree_node_for_add_item_1(request):

    get_tree_node_for_add_item_form = DoGetWFTreeForAddItem(request.POST)

    username = request.user
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {}
    add_this_list = []
    context_dict = context_helper.copy()

    wf_node_pk = WorkflowTree.objects.all().values_list('pk', flat=True)[:1]
    wf_root_node = WorkflowTree.objects.get(pk=wf_node_pk).get_root()
    wf_distant_parent_list = wf_root_node.get_children()

    for item in wf_distant_parent_list:
        add_this = item.get_children().values_list('wf_item_name', flat=True).order_by('wf_item_name')
        add_this_list.extend(add_this)

    context_dict_local.update({'wf_parent_list': add_this_list})

    context_dict.update(context_dict_local)

    if request.method == 'POST':
        if get_tree_node_for_add_item_form.is_valid():
            get_this_node_docs = get_tree_node_for_add_item_form.cleaned_data['get_this_node_docs']

            wf_doc_parent_node = WorkflowTree.objects.get(wf_item_name=get_this_node_docs).get_children()
            wf_doc_parent_proto = wf_doc_parent_node.get(wf_item_is_proto=True)
            wf_doc_parent_proto_uuid = wf_doc_parent_proto.uuid_wf_item
            wf_doc_parent_proto_uuid_string = str(wf_doc_parent_proto_uuid)

            return HttpResponseRedirect(reverse('get_tree_node_for_add_item_2', kwargs={'uuidtreenode': wf_doc_parent_proto_uuid_string}))

        else:
            #TODO FIX THIS
            return

    else:
        return render(request, 'allonsy/forms/wf_tree_select_node_1.html', context_dict, context_instance=RequestContext(request))


def get_tree_node_for_add_item_2(request, uuidtreenode):

    get_tree_node_for_add_item_form = DoGetWFTreeForAddItem(request.POST)

    username = request.user
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {}
    add_this_list = []
    context_dict = context_helper.copy()

    treenode_string_to_uuid = uuid.UUID(uuidtreenode)
    wf_proto = WorkflowTree.objects.get(uuid_wf_item=treenode_string_to_uuid)
    wf_proto_list = wf_proto.get_children().values_list('wf_item_name', flat=True).order_by('wf_item_name')
    add_this_list.extend(wf_proto_list)

    context_dict_local.update({'wf_parent_list': add_this_list})

    context_dict.update(context_dict_local)

    if request.method == 'POST':
        if get_tree_node_for_add_item_form.is_valid():
            get_this_node_docs = get_tree_node_for_add_item_form.cleaned_data['get_this_node_docs']

            wf_doc_parent_node = WorkflowTree.objects.get(wf_item_name=get_this_node_docs)
            wf_doc_parent_proto_uuid = wf_doc_parent_node.uuid_wf_item
            wf_doc_parent_proto_uuid_string = str(wf_doc_parent_proto_uuid)

            return HttpResponseRedirect(reverse('get_edit_tree_workflow_items', kwargs={'uuidtreenode': wf_doc_parent_proto_uuid_string}))

        else:
            #TODO:FIX THIS
            return

    else:
        return render(request, 'allonsy/forms/wf_tree_select_node_2.html', context_dict, context_instance=RequestContext(request))


def get_edit_tree_workflow_items(request, uuidtreenode):

    get_edit_tree_node_for_add_item_form = DoGetWFTreeForAddItem(request.POST)

    username = request.user
    context_helper = get_user_data(request, username)

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {}
    context_dict = context_helper.copy()

    treenode_string_to_uuid = uuid.UUID(uuidtreenode)
    wf_proto = WorkflowTree.objects.get(uuid_wf_item=treenode_string_to_uuid)
    wf_column_dict = wf_proto.get_children()
    counter = 1

    context_dict_local.update({'wf_column_dict': wf_column_dict, 'wf_proto': wf_proto})

    if not wf_column_dict:
        # TODO: return error if there are no columns, or start the column creator
        return HttpResponse('Error! No columns!')

    else:
        for column in wf_column_dict:
            column_pk = column.pk
            this_column = WorkflowTree.objects.get(pk=column_pk)
            context_dict_local.update({'name_for_column_' + str(counter): this_column})
            this_column_uuid_str = str(this_column.uuid_wf_item)
            context_dict_local.update({'uuid_str_for_column_' + str(counter): this_column_uuid_str})
            items_for_column = this_column.get_children()
            context_dict_local.update({'items_for_column_' + str(counter): items_for_column})
            counter += 1

    '''for item in wf_column_dict:
        items_for_column = item.get_children()
        context_dict_local.update({'items_for_column_' + str(item_counter): items_for_column})
        item_counter += 1'''

    context_dict.update(context_dict_local)

    return render(request, 'allonsy/forms/wf_tree_edit_items.html', context_dict, context_instance=RequestContext(request))


def create_new_wf_item_as_child(request, uuidtreenode):
    get_add_wf_tree_item_form = DoAddWFTreeItem(request.POST)

    username = request.user
    treenode_string_to_uuid = uuid.UUID(uuidtreenode)
    wf_parent = WorkflowTree.objects.get(uuid_wf_item=treenode_string_to_uuid)
    wf_doc_ancestors = wf_parent.get_ancestors()

    if wf_parent.level >= 6:
        wf_doc = wf_doc_ancestors.reverse()[1]
    else:
        wf_doc = wf_doc_ancestors.reverse()[0]

    wf_doc_uuid = wf_doc.uuid_wf_item
    wf_doc_uuid_str = str(wf_doc_uuid)

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {}
    context_dict = context_helper.copy()

    if request.method == 'POST':
        if get_add_wf_tree_item_form.is_valid():
            uuid_wf_item = uuid.uuid4()
            wf_item_name = get_add_wf_tree_item_form.cleaned_data['wf_item_name']
            wf_item_text = get_add_wf_tree_item_form.cleaned_data['wf_item_text']
            wf_item_is_active = get_add_wf_tree_item_form.cleaned_data['wf_item_is_active']
            wf_item_owner = username
            wf_item_parent = wf_parent

            do_create_wf_item = WorkflowTree.objects.create(uuid_wf_item=uuid_wf_item,
                                                            wf_item_name=wf_item_name,
                                                            wf_item_text=wf_item_text,
                                                            wf_item_is_active=wf_item_is_active,
                                                            parent=wf_item_parent)

            do_create_wf_item.save()
            do_create_wf_item.wf_item_owner.add(wf_item_owner)

            return HttpResponseRedirect(reverse('get_edit_tree_workflow_items', kwargs={'uuidtreenode': wf_doc_uuid_str}))

        else:
            context_dict_form_errors = {'form': get_add_wf_tree_item_form}
            context_dict_local.update(context_dict_form_errors)
            context_dict.update(context_dict_local)

            return render(request, 'allonsy/forms/wf_tree_create_items.html', context_dict, context_instance=RequestContext(request))

    else:
        return render(request, 'allonsy/forms/wf_tree_create_items.html', context_dict, context_instance=RequestContext(request))


def edit_wf_item_as_child(request, uuiditemnode):
    get_edit_wf_tree_item_form = DoAddWFTreeItem(request.POST)

    username = request.user
    # treenode_string_to_uuid = uuid.UUID(uuidtreenode)
    # wf_parent = WorkflowTree.objects.get(uuid_wf_item=treenode_string_to_uuid)
    wf_parent = WorkflowTree.objects.get(uuid_wf_item=uuiditemnode)
    wf_doc_ancestors = wf_parent.get_ancestors()
    # Check to see if this is a workflow column object (L5) or a workflow item (L6)
    if wf_parent.level >= 6:
        wf_doc = wf_doc_ancestors.reverse()[1]
    else:
        wf_doc = wf_doc_ancestors.reverse()[0]

    wf_doc_uuid = wf_doc.uuid_wf_item
    wf_doc_uuid_str = str(wf_doc_uuid)

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {}
    context_dict = context_helper.copy()

    if request.method == 'POST':
        if get_edit_wf_tree_item_form.is_valid():
            wf_item_name = get_edit_wf_tree_item_form.cleaned_data['wf_item_name']
            wf_item_text = get_edit_wf_tree_item_form.cleaned_data['wf_item_text']
            wf_item_is_active = get_edit_wf_tree_item_form.cleaned_data['wf_item_is_active']

            get_edit_wf_item = WorkflowTree.objects.get(uuid_wf_item=uuiditemnode)

            get_edit_wf_item.wf_item_name = wf_item_name
            get_edit_wf_item.wf_item_text = wf_item_text
            get_edit_wf_item.wf_item_is_active = wf_item_is_active

            get_edit_wf_item.save()

            return HttpResponseRedirect(reverse('get_edit_tree_workflow_items', kwargs={'uuidtreenode': wf_doc_uuid_str}))

        else:
            context_dict_form_errors = {'form': get_edit_wf_tree_item_form}
            context_dict_local.update(context_dict_form_errors)
            context_dict.update(context_dict_local)

            return render(request, 'allonsy/forms/wf_tree_edit_wf_items.html', context_dict, context_instance=RequestContext(request))

    else:
        get_edit_wf_item = WorkflowTree.objects.get(uuid_wf_item=uuiditemnode)

        context_dict_local = {'get_edit_wf_item': get_edit_wf_item}
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/forms/wf_tree_edit_wf_items.html', context_dict, context_instance=RequestContext(request))


def delete_wf_item_as_child(request, uuiditemnode):
    delete_wf_tree_item_form = DoDeleteWFTreeItem(request.POST)

    username = request.user
    # treenode_string_to_uuid = uuid.UUID(uuidtreenode)
    # wf_parent = WorkflowTree.objects.get(uuid_wf_item=treenode_string_to_uuid)
    wf_parent = WorkflowTree.objects.get(uuid_wf_item=uuiditemnode)
    wf_doc_ancestors = wf_parent.get_ancestors()

    if wf_parent.level >= 6:
        wf_doc = wf_doc_ancestors.reverse()[1]
    else:
        wf_doc = wf_doc_ancestors.reverse()[0]

    wf_doc_uuid = wf_doc.uuid_wf_item
    wf_doc_uuid_str = str(wf_doc_uuid)

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {}
    context_dict = context_helper.copy()

    if request.method == 'POST':
        if delete_wf_tree_item_form.is_valid():
            wf_item_do_delete = delete_wf_tree_item_form.cleaned_data['wf_item_do_delete']

            if wf_item_do_delete == 'True':

                get_edit_wf_item = WorkflowTree.objects.get(uuid_wf_item=uuiditemnode)

                get_edit_wf_item.delete()

                return HttpResponseRedirect(reverse('get_edit_tree_workflow_items', kwargs={'uuidtreenode': wf_doc_uuid_str}))

            else:
                # TODO: REPLACE WITH PROPER ERROR MESSAGE
                return HttpResponse("Silly!")

        else:
            context_dict_form_errors = {'form': delete_wf_tree_item_form}
            context_dict_local.update(context_dict_form_errors)
            context_dict.update(context_dict_local)

            return render(request, 'allonsy/forms/wf_tree_create_wf_items.html', context_dict, context_instance=RequestContext(request))

    else:
        get_edit_wf_item = WorkflowTree.objects.get(uuid_wf_item=uuiditemnode)

        context_dict_local = {'get_edit_wf_item': get_edit_wf_item}
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/forms/wf_tree_delete_wf_items.html', context_dict, context_instance=RequestContext(request))


def do_create_wf_instance(request, username, uuidparentnode):

    # bbb020f9-aee0-4a67-bba6-fe56a237dbbf
    # uuidparentnode is the node selected as default for the type of workflow
    # TODO: Ensure that there can be only one default per workflow type
    # TODO: Document that the target node must ALWAYS be right of the Proto node in the tree on account setup
    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {}
    context_dict = context_helper.copy()

    wf_parent = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)
    wf_node_list = wf_parent.get_children()
    wf_proto_parent_node = wf_node_list[0]
    wf_proto_node = WorkflowTree.objects.get(parent=wf_proto_parent_node, wf_item_is_proto=True)
    wf_proto_columns = wf_proto_node.get_children().filter(wf_item_is_active=True)
    wf_target_parent_node = wf_node_list[1]
    wf_target_parent_cat = wf_proto_parent_node.wf_item_proto_category
    today = date.today()
    wf_name_text = str(current_user.first_name + '\'s ' + wf_proto_node.wf_item_name + today.strftime(' (%Y-%b-%d)'))
    wf_target_uuid = uuid.uuid4()

    try:
        wf_target_node = WorkflowTree.objects.create(parent=wf_target_parent_node,
                                                     wf_item_name=wf_name_text,
                                                     wf_item_status='C',
                                                     wf_item_proto_category=wf_target_parent_cat)

        #many-to-many only after object created
        wf_target_node.save()
        wf_target_node.wf_item_owner.add(current_user)

        for column in wf_proto_columns:
            wf_item_name = column.wf_item_name
            wf_item_text = column.wf_item_text
            wf_item_status = 'C'

            wf_target_column = WorkflowTree.objects.create(uuid_wf_item=wf_target_uuid,
                                                           parent=wf_target_node,
                                                           wf_item_name=wf_item_name,
                                                           wf_item_text=wf_item_text,
                                                           wf_item_status=wf_item_status)

            #many-to-many only after object created
            wf_target_column.save()
            wf_target_column.wf_item_owner.add(current_user)

            wf_proto_items = column.get_children()

            for item in wf_proto_items:
                wf_item_name = item.wf_item_name
                wf_item_text = item.wf_item_text
                wf_item_status = 'OFF'

                wf_target_item = WorkflowTree.objects.create(parent=wf_target_column,
                                                             wf_item_name=wf_item_name,
                                                             wf_item_text=wf_item_text,
                                                             wf_item_status=wf_item_status)

                #many-to-many only after object created
                wf_target_item.save()
                wf_target_item.wf_item_owner.add(current_user)

                #TODO:START HERE
        # return HttpResponseRedirect(reverse('get_edit_tree_workflow_items', kwargs={'uuidtreenode': wf_doc_uuid_str}))
        return HttpResponseRedirect(reverse('do_edit_wf_instance', kwargs={'username': username, 'uuidparentnode': wf_target_node.uuid_wf_item}))

    except BaseException as e:
        # TODO: narrow this clause
        return HttpResponse("Error: The report could not be generated. " + str(e))


def do_edit_wf_instance(request, username, uuidparentnode):

    parent_node = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)

    dyn_items_list = get_dyn_items(request, uuidparentnode)
    dyn_columns_list = get_dyn_columns(request, uuidparentnode)
    do_get_wf_instance_form = DoGetWFInstance(request.POST, dyn_items=dyn_items_list)

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {'dyn_columns': dyn_columns_list, 'dyn_items': dyn_items_list}
    context_dict = context_helper.copy()

    if request.method == 'POST':

        if do_get_wf_instance_form.is_valid():

            # Checks if any items are to be completed. If 0, ask whether user wants to submit form
            wf_tbc = 0

            for (name, value) in do_get_wf_instance_form.extra_states():
                get_item = WorkflowTree.objects.get(uuid_wf_item=name)

                if value is True:
                    get_item.wf_item_status = 'ON'
                    get_item.save()

                elif value is False:
                    get_item.wf_item_status = 'OFF'
                    get_item.save()
                    wf_tbc = wf_tbc + 1

                else:
                    return HttpResponse("Error")

            parent_node.wf_item_status = "I"
            parent_node.save()

            if wf_tbc >= 1:

                return HttpResponseRedirect(reverse('do_edit_wf_instance', kwargs={'username': username, 'uuidparentnode': uuidparentnode}))

            else:
                return HttpResponseRedirect(reverse('check_wf_before_complete', kwargs={'username': username, 'uuidparentnode': uuidparentnode}))

        else:
            context_dict_form_errors = {'form': do_get_wf_instance_form}
            context_dict_local.update(context_dict_form_errors)
            context_dict.update(context_dict_local)

            return render(request, 'allonsy/forms/wf_instance_edit.html', context_dict, context_instance=RequestContext(request))

    else:
        context_dict_form_errors = {'form': do_get_wf_instance_form}
        context_dict_local.update(context_dict_form_errors)
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/forms/wf_instance_edit.html', context_dict, context_instance=RequestContext(request))


def do_edit_wf_instance_meta(request, username, uuidparentnode):

    parent_node = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)
    do_edit_wf_instance_meta_form = DoEditWFInstanceMeta(request.POST)

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {'instance_data': parent_node}
    context_dict = context_helper.copy()

    if request.method == 'POST':
        if do_edit_wf_instance_meta_form.is_valid():
            wf_item_name = do_edit_wf_instance_meta_form.cleaned_data['wf_item_name']
            wf_item_text = do_edit_wf_instance_meta_form.cleaned_data['wf_item_text']

            parent_node.wf_item_name = wf_item_name
            parent_node.wf_item_text = wf_item_text

            parent_node.save()

            return HttpResponseRedirect(reverse('roles_onduty', kwargs={'username': username}))

        else:
            return HttpResponse("Error")

    else:
        context_dict_form_errors = {'form': do_edit_wf_instance_meta_form}
        context_dict_local.update(context_dict_form_errors)
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/forms/wf_instance_meta_edit.html', context_dict, context_instance=RequestContext(request))


def do_approve_wf_instance(request, username, uuidparentnode):

    parent_node = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)

    dyn_items_list = get_dyn_items(request, uuidparentnode)
    dyn_columns_list = get_dyn_columns(request, uuidparentnode)
    # do_get_wf_instance_form = DoGetWFInstance(request.POST, dyn_items=dyn_items_list)

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {'dyn_columns': dyn_columns_list, 'dyn_items': dyn_items_list, 'parent_node': parent_node}
    context_dict = context_helper.copy()

    '''if request.method == 'POST':

        if do_get_wf_instance_form.is_valid():

            # Checks if any items are to be completed. If 0, ask whether user wants to submit form
            wf_tbc = 0

            for (name, value) in do_get_wf_instance_form.extra_states():
                get_item = WorkflowTree.objects.get(uuid_wf_item=name)

                if value is True:
                    get_item.wf_item_status = 'ON'
                    get_item.save()

                elif value is False:
                    get_item.wf_item_status = 'OFF'
                    get_item.save()
                    wf_tbc = wf_tbc + 1

                else:
                    return HttpResponse("Error")

            parent_node.wf_item_status = "I"
            parent_node.save()

            if wf_tbc >= 1:

                return HttpResponseRedirect(reverse('do_edit_wf_instance', kwargs={'username': username, 'uuidparentnode': uuidparentnode}))

            else:
                return HttpResponseRedirect(reverse('check_wf_before_complete', kwargs={'username': username, 'uuidparentnode': uuidparentnode}))

        else:
            context_dict_form_errors = {'form': do_get_wf_instance_form}
            context_dict_local.update(context_dict_form_errors)
            context_dict.update(context_dict_local)

            return render(request, 'allonsy/forms/wf_instance_edit.html', context_dict, context_instance=RequestContext(request))

    else:
        context_dict_form_errors = {'form': do_get_wf_instance_form}
        context_dict_local.update(context_dict_form_errors)
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/forms/wf_instance_edit.html', context_dict, context_instance=RequestContext(request))'''

    context_dict.update(context_dict_local)

    return render(request, 'allonsy/wf_instance_approve.html', context_dict, context_instance=RequestContext(request))


def check_wf_before_approve(request, username, uuidparentnode):
    parent_node = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)
    parent_columns = WorkflowTree.objects.filter(parent=parent_node)
    target_items_list = []

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {'parent_node': parent_node}
    context_dict = context_helper.copy()

    urlstatus = 'a'

    for column in parent_columns:
        target_items = column.get_children()
        for item in target_items:
            item_status = item.wf_item_status
            if item_status == 'OFF':
                target_items_list.append(item)
            else:
                pass

    if target_items_list:
        status = "incomplete"
        message = "Some required items are incomplete! Are you sure you want to continue?"

        context_dict_status = {'status': status, 'message': message, 'urlstatus': urlstatus}
        context_dict_local.update(context_dict_status)
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/roles_check_wf_approve.html', context_dict, context_instance=RequestContext(request))

    else:
        status = "complete"
        message = "Are you sure you want to complete this form? You will not be able to edit after this screen."

        context_dict_status = {'status': status, 'message': message, 'urlstatus': urlstatus}
        context_dict_local.update(context_dict_status)
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/roles_check_wf_approve.html', context_dict, context_instance=RequestContext(request))


def check_wf_before_complete(request, username, uuidparentnode):
    parent_node = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)
    parent_columns = WorkflowTree.objects.filter(parent=parent_node)
    target_items_list = []

    context_helper = get_user_data(request, username)
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)
    context_dict_local = {'parent_node': parent_node}
    context_dict = context_helper.copy()

    urlstatus = 's'

    for column in parent_columns:
        target_items = column.get_children()
        for item in target_items:
            item_status = item.wf_item_status
            if item_status == 'OFF':
                target_items_list.append(item)
            else:
                pass

    if target_items_list:
        status = "incomplete"
        message = "Some required items are incomplete! Are you sure you want to continue?"

        context_dict_status = {'status': status, 'message': message, 'urlstatus': urlstatus}
        context_dict_local.update(context_dict_status)
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/roles_check_wf_complete.html', context_dict, context_instance=RequestContext(request))

    else:
        status = "complete"
        message = "Are you sure you want to complete this form? You will not be able to edit after this screen."

        context_dict_status = {'status': status, 'message': message, 'urlstatus': urlstatus}
        context_dict_local.update(context_dict_status)
        context_dict.update(context_dict_local)

        return render(request, 'allonsy/roles_check_wf_complete.html', context_dict, context_instance=RequestContext(request))


def wf_status_update(request, username, statuscode, uuidparentnode):

    parent_node = WorkflowTree.objects.get(uuid_wf_item=uuidparentnode)
    status = statuscode

    if status == 's':

        parent_node.wf_item_status = 'S'
        parent_node.save()

        return HttpResponseRedirect(reverse('roles_onduty', kwargs={'username': username}))

    if status == 'a':

        parent_node.wf_item_status = 'A'
        parent_node.save()

        return HttpResponseRedirect(reverse('roles_dashboard', kwargs={'username': username}))

    if status == 'r':

        parent_node.wf_item_status = 'R'
        parent_node.save()

        return HttpResponseRedirect(reverse('roles_dashboard', kwargs={'username': username}))

    else:

        return HttpResponse("Error")


def do_add_epoch(request):
    do_add_epoch_form = DoAddEpoch(request.POST)

    username = request.user
    epoch_parent_list = Epoch.objects.all().order_by('level', 'epoch_StartDate', 'epoch_Name')
    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    context_dict = {'form': do_add_epoch_form, 'cur_user': current_user, 'req_user': req_user, 'epoch_parent_list': epoch_parent_list}

    if request.method == 'POST':

        if do_add_epoch_form.is_valid():
            epoch_parent = do_add_epoch_form.cleaned_data['epoch_parent']
            epoch_Name = do_add_epoch_form.cleaned_data['epoch_Name']
            epoch_StartDate = do_add_epoch_form.cleaned_data['epoch_StartDate']
            epoch_EndDate = do_add_epoch_form.cleaned_data['epoch_EndDate']

            proto_form = Epoch.objects.create(
                epoch_Name=epoch_Name,
                epoch_StartDate=epoch_StartDate,
                epoch_EndDate=epoch_EndDate,
            )

            proto_form.save()

            proto_form.parent = Epoch.objects.get(uuid_epoch=epoch_parent)

            proto_form.save()

            return render(request, 'allonsy/user.html')

        else:
                # Return a 'disabled account' error message
            return render(request, 'allonsy/forms/add-epoch.html', context_dict, context_instance=RequestContext(request))
            #return HttpResponseRedirect("Failed validation")

    else:
            # Return a 'disabled account' error message
        return render(request, 'allonsy/forms/add-epoch.html', context_dict, context_instance=RequestContext(request))


def assoc_user_loc_res_init(request):
    do_get_user_select_form = DoGetUserSelectForm(request.Post)

    campus_objects = Location.objects.filter(location_type='C')
    student_userext_list = UserExtension.objects.filter(user_type='T')
    student_list = []

    for student in student_userext_list:
        student_username = student.user.username
        student_user_pk = User.objects.filter(username=student_username).values_list('pk', flat=True)
        student_list.extend(student_user_pk)

    student_user_objects = User.objects.filter(pk__in=student_list)

    context_dict = {'form': do_get_user_select_form, 'campus_objects': campus_objects, 'student_user_objects': student_user_objects}

    if request.method == 'POST':
        if do_get_user_select_form.is_valid():
            student_pk = do_get_user_select_form.cleaned_data['user_pk']
            uuid_student_campus = do_get_user_select_form.cleaned_data['campus_uuid']

            userpk = User.objects.get(pk=student_pk)
            uuidlocnode = uuid_student_campus

            return HttpResponseRedirect(reverse('do_assoc_loc_residence', kwargs={'userpk': userpk, 'uuidlocnode': uuidlocnode}))

        else:
            HttpResponse("Error - invalid")

    else:
        return render(request, 'allonsy/forms/add-epoch.html', context_dict, context_instance=RequestContext(request))


def check_if_loc_residence(request, userpk, uuidlocnode):
    do_get_loc_form = DoGetLocForm(request.POST)

    current_location = Location.objects.get(uuid_location=uuidlocnode)

    context_dict = {'form': do_get_loc_form, 'curr_location': current_location}

    if request.method == 'POST':
        if do_get_loc_form.is_valid():
            uuid_location = do_get_loc_form.cleaned_data['uuid_location']

            new_location = Location.objects.filter(uuid_location=uuid_location).values_list('uuid_location', flat=True)

            if uuid_location.location_type is not 'L':
                return HttpResponseRedirect(reverse('check_if_loc_residence', kwargs={'userpk': userpk, 'uuidlocnode': new_location}))

            elif uuid_location.location_type is 'L':
                return HttpResponseRedirect(reverse('do_assoc_loc_residence', kwargs={'userpk': userpk, 'uuidlocnode': new_location}))

            else:
                HttpResponse("Unexpected error")

    else:

        if current_location.location_type is not 'L':
            # TODO: Add a check if descendant count > 0. If it is not, ak user to create a descendant

            current_location_children = current_location.get_children()
            filter_possible_desc = current_location.get_descendants().filter(location_type='L')

            context_dict_local = {'curr_loc_children': current_location_children, 'filter': filter_possible_desc}
            context_dict.update(context_dict_local)

            return render(request, 'allonsy/forms/add-epoch.html', context_dict, context_instance=RequestContext(request))

        elif current_location.location_type is 'L':

            return HttpResponseRedirect(reverse('do_assoc_loc_residence', kwargs={'userpk': userpk, 'uuidlocnode': uuidlocnode}))

        else:
            return HttpResponse("Unexpected error")


def do_assoc_loc_residence(request, userpk, uuidlocnode):

    return HttpResponse("OK!")


def roles_do_update_duty_status(request, username, status, role):
    #TODO: Make this a form. Until then, always ensure that the view accepts /only/ the expected parameters
    #TODO: RAs should not be able to check in as on duty. Add a check to the group defined as residence life for is_staff permissions

    current_user_obj, current_user, current_userextension, current_user_acct, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username)

    context_dict = {'cur_user': current_user, 'req_user': req_user}

    if status == 'in':
        if role == 'duty':
            usrext = UserExtension.objects.get(user=request.user)
            usrext.user_checkin_onduty = True

            usrext.save()

        elif role == 'call':
            usrext = UserExtension.objects.get(user=request.user)
            usrext.user_checkin_oncall = True

            usrext.save()

        else:
            return HttpResponseRedirect(reverse('roles_dashboard', kwargs={'username': request.user}))

    elif status == 'out':
        if role == 'duty':
            usrext = UserExtension.objects.get(user=request.user)
            usrext.user_checkin_onduty = False

            usrext.save()

        elif role == 'call':
            usrext = UserExtension.objects.get(user=request.user)
            usrext.user_checkin_oncall = False

            usrext.save()

        else:
            return HttpResponseRedirect(reverse('roles_dashboard', kwargs={'username': request.user}))

    else:
        # return HttpResponseRedirect(reverse('roles_dashboard', kwargs={'username': request.user}))
        return HttpResponse("ta-da")

    return HttpResponseRedirect(reverse('roles_dashboard', kwargs={'username': request.user}))