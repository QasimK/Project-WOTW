from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate

from wotw_project.forms import AccountRegistrationForm, LoginForm
from game.models import Character
from game.views import introduction


def main_page(request):
    if request.user.is_authenticated():
        data = {}
        return render_to_response('index.html', data,
                                  context_instance=RequestContext(request))
    else:
        if request.method == 'GET':
            login_form = AuthenticationForm(request)
    
        elif request.method == 'POST':
            login_form = AuthenticationForm(request, data=request.POST)
            print("test")
            if login_form.is_valid():
                print("test2")
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect(introduction)
                    else:
                        # TODO: Disabled account
                        pass
        
        data = {
            'login_form': login_form
        }
        return render_to_response('index.html', data,
                              context_instance=RequestContext(request))

def main_page2(request):
    if request.method == "POST": #Data was passed through
        #Create the bound form with the data the user created
        reg_form = AccountRegistrationForm(request.POST)
        if reg_form.is_valid():
            #Process data
            username = reg_form.cleaned_data["account_name"]
            password = reg_form.cleaned_data["account_password"]
            #username, email, password
            new_user = User.objects.create_user(username, "", password)
            
            #Create their character
            Character.make_new_character(new_user)
            
            return redirect(reverse(introduction))
    else:
        #A new unbound form
        reg_form = AccountRegistrationForm()
    
    data = {
        "registration_form": reg_form,
    }
    return render_to_response("index.html", data,
                              context_instance=RequestContext(request))
    #RequestContext handles CSRF protection for forms




"""def login_page(request):
    login_msg = ""
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            #Process login details and login
            username = login_form.cleaned_data["account_name"]
            password = login_form.cleaned_data["account_password"]
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(wotw_src.game_website.views.introduction)
                else:
                    login_msg = "Your account has been disabled"
            else:
                login_msg = "Wrong username and password"
    else:
        login_form = LoginForm()
        
    data = {
        "login_form": login_form,
        "login_form_action": reverse(login_page), #Come back here
        "login_msg": login_msg,
    }
    return render_to_response("login.html", data,
                              context_instance=RequestContext(request))
"""
