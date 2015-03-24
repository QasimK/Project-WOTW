from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth import login, authenticate

from game.models import Character

def main_page(request):
    data = {}
    if request.user.is_authenticated(): # Change username/password
        set_password_form = SetPasswordForm(request.user,
                                            data=(request.POST or None))
        if request.method == 'POST' and set_password_form.is_valid():
            set_password_form.save()
            data['password_change_msg'] = "Password has successfully changed."
        
        data['set_password_form'] = set_password_form
    
    else: # Login form
        login_form = AuthenticationForm(request, data=(request.POST or None))
        if request.method == 'POST' and login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            
            # To prevent people to log into temporary passwordless accounts:
            if len(password): 
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect(reverse('game:index'))
            
        data['login_form'] = login_form
    
    return render(request, 'index.html', data)


def start_game(request):
    username = 'Account' + str(User.objects.count())
    password = ''
    User.objects.create_user(username, password=password)
    user = authenticate(username=username, password=password)
    login(request, user)
    
    Character.make_new_character(user)
    return redirect(reverse('game:index'))

def save_account(request):
    pass
