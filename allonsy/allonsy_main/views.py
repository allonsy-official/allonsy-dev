from django.shortcuts import render, render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from allonsy_main.models import UserExtension, User


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
def usr(request):
    current_user = request.user
    current_user_id = current_user.id
    user_extension = UserExtension.objects.get(user=current_user_id)
    user_phone = user_extension.user_phone_value
    context_dict = {'user_extension': user_phone, }
    return render(request, 'allonsy/user.html', context_dict)


def app(request):
    return render(request, 'allonsy/app.html')
