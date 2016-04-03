from django.shortcuts import render, render_to_response, RequestContext, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax

from allonsy_main.forms import DoAddAccount, DoAddOrganization, DoAddLocation, DoAssocOrganization, DoAssocOrganizationUser
from allonsy_main.models import UserExtension, User, Organization, TreeOrganization, RelationOrganizationUser


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
                return HttpResponseRedirect('/user/')
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
    current_user = request.user
    req_user = User.objects.get(username=username)
    req_userextension = UserExtension.objects.get(user=req_user)
    req_user_uuid = req_userextension.uuid_user
    req_user_orgs = RelationOrganizationUser.objects.all().filter(uuid_user=req_user_uuid)

    context_dict = {'req_user': req_user, 'req_userextension': req_userextension, 'orgs': req_user_orgs}
    # return render(request, 'allonsy/user.html', context_dict)
    return render(request, 'allonsy/user.html', context_dict, context_instance=RequestContext(request))



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
                do_create_object = RelationOrganizationUser.objects.create(uuid_account=fk_val, relation_name=assoc_relation_name, uuid_user=assoc_usr)
                do_create_object.save()
                do_create_object.uuid_org.add(assoc_org)

            return render('allonsy/user.html')

        else:
            # Return a 'disabled account' error message
            return render_to_response('allonsy/associate-user.html', {'form': do_assoc_organization_user_form})
            # return HttpResponse('Fail 1')

    else:
            # Return a 'disabled account' error message
       #return render_to_response('allonsy/associate-user.html', {'form': do_assoc_organization_user_form})
        return HttpResponse('Fail 2')

def app(request):
    return render(request, 'allonsy/app.html')
