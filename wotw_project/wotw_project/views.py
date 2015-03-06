from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate

from game.models import Character

def main_page(request):
    data = {}
    if not request.user.is_authenticated():
        if request.method == 'GET':
            login_form = AuthenticationForm(request)
    
        elif request.method == 'POST':
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                
                # To prevent people to log into temporary passwordless accounts:
                if len(password): 
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    return redirect(reverse('game:index'))
            
        data['login_form'] = login_form
    
    return render_to_response('index.html', data,
                              context_instance=RequestContext(request))

def start_game(request):
    username = 'Account' + str(User.objects.count())
    password = ''
    User.objects.create_user(username, password=password)
    user = authenticate(username=username, password=password)
    login(request, user)
    
    Character.make_new_character(user)
    return redirect(reverse('game:index'))
