'''
Created on 5 Aug 2013

@author: Qasim
'''

import random

from game import models

#@view_required("village-in", "village-explore-nothing", "village-in-market")
#@allowed_exit_views("village-found-gold", "village-explore-nothing",
#                    "generic-fighting")
def village_explore(char, post):
    from game.views import ActionError
    
    #Get rid of any current GVPs
    for gvp in char.get_gvps().all():
        gvp.delete()
    
    #Generate a random event
    def eve_found_gold():
        char.game_view = "village-found-gold"
        
        #Amount found
        randgold = min(max(int(random.gauss(10, 3)), 0), 20)
        
        char.gold += randgold
        char.save()
        
        randnum = random.randint(0, 1000000)
        text_gvp = models.GameViewProperty(char=char,
            name="text_selection", value=str(randnum))
        text_gvp.save()
        
        gold_gvp = models.GameViewProperty(char=char,
            name="gold", value=str(randgold))
        gold_gvp.save()
        
    def eve_nothing_much():
        char.game_view = "village-explore-nothing"
        char.save()
        
        #text_selection
        randtext = random.randint(0, 1000000)
        models.GameViewProperty.objects.create(
            char=char, name="text_selection", value=randtext)
    
    def eve_fight():
        potential_monsters = [
            "Rabid Dog",
            "Lone Wolf",
            "Thief",
            "Vicious Bear"
        ]
        
        monster = random.choice(potential_monsters)
        char.start_fight(monster)
        
        #Create the return location
        models.GameViewProperty.objects.create(
            char=char, name="return_loc", value="village-in")
        
        char.game_view = "generic-fighting"
        char.save()
        
    def eve_heal():
        pass
    def eve_found_item():
        pass
    
    events = {
        eve_found_gold: 60,
        eve_nothing_much: 100,
        eve_fight: 400,
        eve_heal: 0,
        eve_found_item: 0,
    }
    
    max_chance = sum(events.itervalues())
    roll = random.randint(0, max_chance-1)
    
    for event_function, chance in events.iteritems():
        roll -= chance
        if roll < 0:
            return event_function()
    
    err = "Major error: Village explore did not give any event!"
    raise ActionError(err)


#@view_required("village-explore-nothing")
#@allowed_exit_views("village-in")
def village_return(char, post):
    char.game_view = "village-in"
    char.save()
    
    for gvp in char.get_gvps().all():
        gvp.delete()


#@view_required("village-found-gold")
#@allowed_exit_views("village-in")
def village_return_from_found_gold(char, post):
    char.game_view = "village-in"
    char.save()
    
    for gvp in char.get_gvps().all():
        gvp.delete()


#@view_required("village-in-market")
#@allowed_exit_views("generic-shopping")
def village_goto_general_shop(char, post):
    char.game_view = "generic-shopping"
    char.save()
    
    #GVPs
    shop = models.Shop.objects.get(name="Village Shop")
    shop_name = models.GameViewProperty(char=char, name="shop_name",
                                        value=shop)
    return_loc = models.GameViewProperty(char=char, name="return_location",
                                         value="village-in-market")
    
    shop_name.save()
    return_loc.save()

#@view_required("village-in-market")
#@allowed_exit_views("generic-shopping")
def village_goto_herb_shop(char, post):
    char.game_view = "generic-shopping"
    char.save()
    
    #GVPs
    shop = models.Shop.objects.get(name="Village Herbology Store")
    shop_name = models.GameViewProperty(char=char, name="shop_name",
                                        value=shop)
    return_loc = models.GameViewProperty(char=char, name="return_location",
                                         value="village-in-market")
    
    shop_name.save()
    return_loc.save()


#@view_required("village-in")
#@allowed_exit_views("village-in-market")
def village_goto_market(char, post):
    char.game_view = "village-in-market"
    char.save()

#@view_required("village-in-market")
#@allowed_exit_views("village-in")
def village_leave_market(char, post):
    char.game_view = "village-in"
    char.save()
