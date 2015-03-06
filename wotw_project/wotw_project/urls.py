from django.conf.urls import patterns, include, url
from django.contrib import admin

from wotw_project import views
import game.urls as game_urls

#wotw_extras template tags
from django import template
template.add_to_builtins('game.templatetags.wotw_extras')


urlpatterns = patterns('',
    url(r'^$', views.main_page),
    
    url(r'^game/', include(game_urls)),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
