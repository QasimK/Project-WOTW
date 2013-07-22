'''
Created on 5 Jul 2011

@author: Qasim
'''

import models
from django.conf import settings

def wotw_processor(request):
    """Add character and debug data to each template
    
    These are available as char and debug."""
    
    additional_info = {}
    if request.user.is_authenticated():
        try:
            char = models.Character.objects.get(user_account=request.user)
        except models.Character.DoesNotExist:
            return {}
        
        additional_info["char"] = char
    
        if settings.DEBUG:
            debug_char_view = "Game view: " + char.game_view
            debug_char_view += "<br />Game view properties: "
            gvps = char.get_gvps().all()
            if gvps:
                debug_char_view += "<ul>"
                for gvp in gvps:
                    debug_char_view += "<li>%s: %s</li>"%(gvp.name, gvp.value)
                debug_char_view += "</ul>"
            else:
                debug_char_view += "None"
            
            additional_info["DEBUG_CHAR_VIEW"] = debug_char_view
    
    return additional_info
