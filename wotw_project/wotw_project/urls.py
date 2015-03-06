from django.conf.urls import patterns, include, url
from django.contrib import admin

from wotw_project import views
import game.urls as game_urls

#wotw_extras template tags
from django import template
template.add_to_builtins('game.templatetags.wotw_extras')


urlpatterns = patterns('',
    url(r'^$', views.main_page, name='index'),
    url(r'^start/$', views.start_game, name='start_game'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    
    url(r'^game/', include(game_urls, namespace='game', app_name='game')),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
