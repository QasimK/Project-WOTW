from django.conf.urls import patterns

from game.views import (
    game_view_resolver, game_action_resolver,
    char_inventory, crafting,
    introduction, game_error, delete_message
)

urlpatterns = patterns('',
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
)

urlpatterns += patterns('',
    (r'^game_view$', game_view_resolver),
    (r'^game_action$', game_action_resolver),
    
    (r'^inventory/$', char_inventory),
    (r'^crafting/$', crafting),
    
    #Other
    (r'^$', introduction),
    (r'^error/$', game_error),
    (r'^delete_message/(?P<msg_num>\d+)/$', delete_message),
)
