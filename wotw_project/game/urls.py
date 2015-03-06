from django.conf.urls import patterns, url

from game.views import (
    game_view_resolver, game_action_resolver,
    char_inventory, crafting,
    game_error, delete_message
)

urlpatterns = patterns('',
    url(r'^$', game_view_resolver, name='index'),
    url(r'^game_action$', game_action_resolver, name='action'),
    
    url(r'^inventory/$', char_inventory, name='inventory'),
    url(r'^crafting/$', crafting, name='crafting'),
    
    #Other
    url(r'^error/$', game_error, name='error'),
    url(r'^delete_message/(?P<msg_num>\d+)/$', delete_message,
        name='delete_message'),
)
