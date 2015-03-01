from django.conf.urls import patterns, include, url
from django.contrib import admin

import game.urls as game_urls
from main_website.views import main_page

#wotw_extras template tags
from django import template
template.add_to_builtins('game.templatetags.wotw_extras')


urlpatterns = patterns('',
    url(r'^$', main_page),
    url(r'^login/$', 'django.contrib.auth.views.login',
                        {'template_name': 'login.html'}),
    
    url(r'^game/', include(game_urls)),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
