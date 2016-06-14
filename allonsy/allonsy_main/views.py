from django.shortcuts import render, render_to_response, RequestContext, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Q
from django_ajax.decorators import ajax

from allonsy_main.forms import DoAddAccount, DoAddOrganization, DoAddLocation, DoAssocOrganization, DoAssocOrganizationUser, DoEditUserProfile, DoEditUserInfoContact, DoEditUserEmergencyContact, DoSendReplyMessage
from allonsy_main.models import Account, UserExtension, User, UserProfile, Organization, TreeOrganization, RelationOrganizationUser, UserInteraction, UserAlert


#Helper functions
#TODO: middleware?

def get_user_data(request, username, account):
    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_account = Account.objects.get(account_url_name=account)
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_acct = req_userextension.uuid_account
    req_user_uuid = req_userextension.uuid_user

    context_helper = {'current_user_obj': current_user_obj,
                      'cur_user': current_user,
                      'current_userextension': current_userextension,
                      'current_user_acct': current_user_acct,
                      'req_account': req_account,
                      'req_user': req_user,
                      'req_userextension': req_userextension,
                      'req_user_acct': req_user_acct,
                      'req_user_uuid': req_user_uuid
                      }

    return context_helper


def get_user_data_objects(request, username, account):
    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_account = Account.objects.get(account_url_name=account)
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_acct = req_userextension.uuid_account
    req_user_uuid = req_userextension.uuid_user

    return current_user_obj, current_user, current_userextension, current_user_acct, req_account, req_user, req_userextension, req_user_acct, req_user_uuid


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
        user_extension = UserExtension.objects.get(user=user)
        user_account = Account.objects.get(account_name=user_extension.uuid_account)
        user_account_url = user_account.account_url_name
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/'+str(user_account_url)+'/user/'+str(user))
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
def user_admin(request, account):

    username = request.user

    context_helper = get_user_data(request, username, account)

    current_user_obj, current_user, current_userextension, current_user_acct, req_account, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username, account)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    context_dict_local = {'orgs_primary': req_user_orgs_primary}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    if str.lower(current_user_acct.account_url_name) == str.lower(req_account.account_url_name):

        if current_user_acct == req_user_acct:

            #TODO: CHANGE BACK TO USER
            return render(request, 'allonsy/user_admin_main.html', context_dict, context_instance=RequestContext(request))

        else:
            # Return a 'disabled account' error message
            return HttpResponse("Disabled")

    else:
        return HttpResponse("Account not available to this user")


@login_required
def usr(request):
    current_user = request.user
    current_user_id = current_user.id
    user_extension = UserExtension.objects.get(user=current_user_id)
    user_phone = user_extension.user_phone_value
    context_dict = {'user_extension': user_phone, }
    return render(request, 'allonsy/user.html', context_dict)


@login_required
def resolve_user_url(request, username, account):
    context_helper = get_user_data(request, username, account)

    current_user_obj, current_user, current_userextension, current_user_acct, req_account, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username, account)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)
    context_dict_local = {'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)
    # return render(request, 'allonsy/user.html', context_dict)

    if str.lower(current_user_acct.account_url_name) == str.lower(req_account.account_url_name):

        if current_user_acct == req_user_acct:

            #TODO: CHANGE BACK TO USER
            return render(request, 'allonsy/user_main.html', context_dict, context_instance=RequestContext(request))

        else:
            # Return a 'disabled account' error message
            return HttpResponse("Disabled")

    else:
        return HttpResponse("Account not available to this user")


@login_required
def edit_user_url(request, username, account):

    context_helper = get_user_data(request, username, account)

    current_user_obj, current_user, current_userextension, current_user_acct, req_account, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username, account)

    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)
    context_dict_local = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme}
    # return render(request, 'allonsy/user.html', context_dict)

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    if str.lower(current_user_acct.account_url_name) == str.lower(req_account.account_url_name):

        if current_user_acct == req_user_acct:

            return render(request, 'allonsy/forms/edituser.html', context_dict, context_instance=RequestContext(request))

        else:
            # Return a 'disabled account' error message
            return HttpResponse("Disabled")

    else:
        return HttpResponse("Account not available to this user")

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
def do_add_account(request, username):
    do_add_account_form = DoAddAccount(request.POST)
    current_user = User.objects.get(username=username)

    context_dict = {'form': do_add_account_form, 'cur_user': current_user}

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
def do_add_organization(request, username):
    do_add_organization_form = DoAddOrganization(request.POST)
    current_user = User.objects.get(username=username)

    context_dict = {'form': do_add_organization_form, 'cur_user': current_user}

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
def do_get_user_alerts(request, username, account):

    context_helper = get_user_data(request, username, account)

    current_user_obj, current_user, current_userextension, current_user_acct, req_account, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username, account)

    new_user_interactions = UserInteraction.objects.all().filter(interaction_target=current_user, interaction_status='O')
    count_new_user_interactions = new_user_interactions.count
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    current_user_interactions = UserAlert.objects.all().filter(Q(interaction_target=current_user), Q(interaction_direction='R'), Q(interaction_status='O') | Q(interaction_status='I'))

    context_dict_local = {'cur_user_interacts': current_user_interactions, 'orgs_primary': req_user_orgs_primary, 'count_new_user_interactions': count_new_user_interactions}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    return render(request, 'allonsy/user_interactions.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_get_user_interactions(request, username, account):

    context_helper = get_user_data(request, username, account)

    current_user_obj, current_user, current_userextension, current_user_acct, req_account, req_user, req_userextension, req_user_acct, req_user_uuid = get_user_data_objects(request, username, account)

    new_user_interactions = UserInteraction.objects.all().filter(interaction_target=current_user, interaction_status='O')
    count_new_user_interactions = new_user_interactions.count
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    current_user_interactions = UserInteraction.objects.all().filter(Q(interaction_target=current_user), Q(interaction_direction='R'), Q(interaction_status='O') | Q(interaction_status='I'))

    context_dict_local = {'cur_user_interacts': current_user_interactions, 'orgs_primary': req_user_orgs_primary, 'count_new_user_interactions': count_new_user_interactions}

    context_dict = context_helper.copy()
    context_dict.update(context_dict_local)

    return render(request, 'allonsy/user_interactions.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_get_user_sent(request, username):
    current_user = User.objects.get(username=request.user)
    new_user_interactions = UserInteraction.objects.all().filter(interaction_target=current_user, interaction_status='O')
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
    current_user_sent = UserInteraction.objects.all().filter(Q(interaction_sender=current_user), Q(interaction_direction='S'))

    context_dict = {'cur_user': current_user,  'req_user': req_user, 'req_userextension': req_userextension, 'cur_user_interacts': current_user_sent, 'orgs_primary': req_user_orgs_primary, 'count_new_user_interactions': count_new_user_interactions}

    return render(request, 'allonsy/user_interactions.html', context_dict, context_instance=RequestContext(request))


@login_required
def do_send_reply_message(request, username, uuidmsg):
    do_send_reply_message_form = DoSendReplyMessage(request.POST)

    current_user = User.objects.get(username=request.user)
    new_user_interactions = UserInteraction.objects.all().filter(interaction_target=current_user, interaction_status='O')
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
    this_user_interaction = UserInteraction.objects.get(uuid_interaction=uuidmsg)
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
            interaction_direction_target = 'R'
            interaction_direction_sender = 'S'

            this_user_interaction.interaction_status = 'I'
            this_user_interaction.save()

            #Create first of two ledger records

            do_create_reply_message_1 = UserInteraction.objects.create(interaction_subject=interaction_subject,
                                                                       interaction_text=interaction_text,
                                                                       interaction_type=interaction_type,
                                                                       interaction_status=interaction_status,
                                                                       interaction_direction=interaction_direction_target)

            #many-to-many only after object created
            do_create_reply_message_1.save()
            do_create_reply_message_1.interaction_target.add(interaction_target)
            do_create_reply_message_1.interaction_sender.add(current_user)

            #Create second of two ledger records

            do_create_reply_message_2 = UserInteraction.objects.create(interaction_subject=interaction_subject,
                                                                       interaction_text=interaction_text,
                                                                       interaction_type=interaction_type,
                                                                       interaction_status=interaction_status,
                                                                       interaction_direction=interaction_direction_sender)

            #many-to-many only after object created
            do_create_reply_message_2.save()
            do_create_reply_message_2.interaction_target.add(interaction_target)
            do_create_reply_message_2.interaction_sender.add(current_user)

            return HttpResponseRedirect(reverse('do_get_user_interactions', kwargs={'username': username}))

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
    this_user_interaction = UserInteraction.objects.get(uuid_interaction=uuidmsg)
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
def do_edit_user_profile(request, username, account):
    do_edit_user_profile_form = DoEditUserProfile(request.POST)

    current_user_obj = request.user
    current_user = User.objects.get(username=request.user)
    current_userextension = UserExtension.objects.get(user=current_user_obj)
    current_user_acct = current_userextension.uuid_account
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_user_acct = req_userextension.uuid_account
    req_account = Account.objects.get(account_url_name=account)
    req_orgs_affil = Organization.objects.filter(org_type_special='X')
    req_user_orgs_affil = RelationOrganizationUser.objects.values('relation_name', 'relation_url').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil)
    req_user_orgs_primary = RelationOrganizationUser.objects.values('relation_name').all().filter(uuid_user=req_user_uuid, uuid_org__in=req_orgs_affil, relation_is_primary=True)
    req_profile_aboutme = UserProfile.objects.get(uuid_user=req_user_uuid)

    context_dict = {'cur_user': current_user, 'req_user': req_user, 'req_userextension': req_userextension, 'orgs_affil': req_user_orgs_affil, 'orgs_primary': req_user_orgs_primary, 'profile_aboutme': req_profile_aboutme}

    if request.method == 'POST':
        if str.lower(current_user_acct.account_url_name) == str.lower(req_account.account_url_name):
            if do_edit_user_profile_form.is_valid():
                profile_aboutme = do_edit_user_profile_form.cleaned_data['profile_aboutme']

                do_edit_profile_object = UserProfile.objects.get(uuid_user=req_userextension)
                do_edit_profile_object.profile_aboutme = profile_aboutme
                do_edit_profile_object.save()

                return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username, 'account': account}))

            else:
                return HttpResponseRedirect(reverse('resolve_user_url', kwargs={'username': username, 'account': account}))

        else:
            return HttpResponse("Account not available to this user")

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


def app(request):
    return render(request, 'allonsy/app.html')
