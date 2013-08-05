'''
Created on 5 Aug 2013

@author: Qasim
'''

from django.shortcuts import redirect

from wotw_project.game import models, item_actions

def create_error(char, err, level=0):
    """Create an error with a priority.
    
    0-4 Normal error (eg. User did it by accident but it is not valid)
    5-9 Major error (eg. My fault or user is poking around)
    10+ ???
    
    Note: A redirect may be returned which you should prioritise.
    (ie. return the redirect we give you)
    """
    from wotw_project.game.views import game_error
    models.Message.objects.create(character=char, body=err)
    if level >= 5:
        return redirect(game_error)


def a_example(char, post):
    assert isinstance(char, models.Character)
    assert isinstance(post, dict)
    

