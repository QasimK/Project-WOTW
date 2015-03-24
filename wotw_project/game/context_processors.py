from django.conf import settings

from game.models import Character

def wotw_processor(request):
    """Pass additional info to every template
    
    Add:
        char: character object
        is_account_saved: has user set a password?
        DEBUG_CHAR_VIEW: debug data HTML
    """
    
    info = {}
    if request.user.is_authenticated():
        try:
            char = Character.objects.get(user_account=request.user)
        except Character.DoesNotExist:
            return {}
        
        info["char"] = char
        info['is_account_saved'] = not request.user.check_password('')
        
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
            
            info["DEBUG_CHAR_VIEW"] = debug_char_view
    
    return info
