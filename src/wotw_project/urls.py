from django.conf.urls import *

import game.urls as game_urls
from main_website.views import main_page

#wotw_extras template tags
from django import template
template.add_to_builtins('game.templatetags.wotw_extras')

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', main_page),
    (r'^login/$', 'django.contrib.auth.views.login',
                        {'template_name': 'login.html'}),
    
    (r'^game/', include(game_urls)),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
