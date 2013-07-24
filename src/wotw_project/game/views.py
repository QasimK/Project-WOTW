'''
Created on 19 Jan 2011

@author: Qasim
'''

import random, os
from functools import wraps

from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

from wotw_project.game import models, item_actions
from wotw_project.game.models import RecipeIngredientInfo

"""
Note:
    context_instance=RequestContext
    RequestContext required to pass in user and messages to template
"""

class IncorrectViewName(RuntimeError):
    def __init__(self, viewname):
        self.viewname = viewname
    def __str__(self):
        return "Incorrect View Name: %s"%self.viewname


def get_char(request):
    """Return user's character object"""
    #print request.user.character_set.all()[0]
    return models.Character.objects.get(user_account=request.user)

def create_msg(char, msg):
    """Just a message"""
    models.Message.objects.create(character=char, body=msg)

def create_error(char, err, level=0):
    """Create an error with a priority.
    
    0-4 Normal error (eg. User did it by accident but it is not valid)
    5-9 Major error (eg. My fault or user is poking around)
    10+ ???
    
    Note: A redirect may be returned which you should prioritise.
    (ie. return the redirect we give you)
    """
    
    models.Message.objects.create(character=char, body=err)
    if level >= 5:
        return redirect(game_error)


game_map_loc = os.path.join(settings.GAME_MAP_LOCATION, "game_map.txt")
if settings.DEBUG:
    os.remove(game_map_loc)

#Decorator
def view_required(*views):
    """Specify that specific game-views (given as strings) are required
    for the character for this ACTION to be valid."""
    
    for view in views:
        if view != "*" and view not in registered_views.keys():
            raise IncorrectViewName(view)
    
    def wrap_func(func):
        if settings.DEBUG:
            with open(game_map_loc, 'a') as f:
                out = [func.__name__+"\n", "Views Required:\n"]
                for view in views:
                    out.append(view+"\n")
                out.append("\n")
                f.writelines(out)
        
        #The actual wrapper for the function:
        @wraps(func)
        def new_func(request, *args, **kwargs):
            char = get_char(request)
            char_view = char.game_view
            if char_view not in views:
                msg="Game-action (%s) cannot occur if character is in incorrect\
                    game-view (%s). You shouldn't see this error."%(
                        "F:"+func.__name__, char_view)
                redir = create_error(char, msg, 5)
                if redir:
                    return redir
            else:
                return func(request, *args, **kwargs)
        
        @wraps(func)
        def anyviewallowed_func(request, *args, **kwargs):
            char = get_char(request)
            char_view = char.game_view
            if char_view not in registered_views.keys():
                msg="Game-action (%s) cannot occur if character is in an\
                    unregistered game-view (%s). You shouldn't see this error."\
                        %("F:"+func.__name__, char_view)
                redir = create_error(char, msg, 5)
                if redir:
                    return redir
            else:
                return func(request, *args, **kwargs)
        
        if "*" in views:
            return anyviewallowed_func
        else:
            return new_func
    
    return wrap_func


#Game Action func Decorator
def allowed_exit_views(*views):
    """Specify that specific game-views (given as strings) are the only
    game-views allowed at the end of the view for this action to be valid.
    
    Note '*' means any registered view"""
    
    for view in views:
        if view != "*" and view not in registered_views.keys():
            raise IncorrectViewName(view)
    
    def wrap_func(func):
        if settings.DEBUG:
            with open(game_map_loc, 'a') as f:
                out = [func.__name__+"\n", "Views Allowed on Exit:\n"]
                for view in views:
                    out.append(view+"\n")
                out.append("\n")
                f.writelines(out)
        
        #The actual wrapper for the function:
        @wraps(func)
        def new_func(request, *args, **kwargs):
            returnvalue = func(request, *args, **kwargs)
            
            char = get_char(request)
            char_view = char.game_view
            if char_view not in views:
                msg="Game-action (%s) set a disallowed\
                    game-view (%s). You shouldn't see this error."%(
                        "F:"+func.__name__, char_view)
                redir = create_error(char, msg, 5)
                if redir:
                    return redir
            else:
                return returnvalue
        
        @wraps(func)
        def anyviewallowed_func(request, *args, **kwargs):
            returnvalue = func(request, *args, **kwargs)
            
            char = get_char(request)
            char_view = char.game_view
            if char_view not in registered_views.keys():
                msg="Game-action (%s) set an invalid/unregistered\
                    game-view (%s). You shouldn't see this error."%(
                        "F:"+func.__name__, char_view)
                redir = create_error(char, msg, 5)
                if redir:
                    return redir
            else:
                return returnvalue
        
        if "*" in views: #No changes required
            return anyviewallowed_func
        else:
            return new_func
    
    return wrap_func

    

#TODO: Item actions
def char_inventory(request):
    char = get_char(request)
    if char.inventory_mode in (models.Character.INV_FULL_ACCESS,
                               models.Character.INV_VIEW_ONLY):
        data = {
            "inv_cv": char.inventory.get_condensed_view()
        }
        return render(request, "game/generic/inventory.html", data)
    else:
        return render(request, "game/generic/inventory.html")

#---Global Views
def crafting(request):
    char = get_char(request)
    if char.inventory_mode in (char.INV_FULL_ACCESS, char.INV_VIEW_ONLY):
        #['recipe', [('ingredient', '#num, 'has')], [('product', '#num')]]
        known_recipes = []
        for recipe in char.known_recipes.all():
            ingredients_list = []
            can_make = True
            for ingredient in recipe.ingredients.all():
                info = ingredient.recipeingredientinfo_set.get(recipe=recipe)
                quantity = info.quantity
                if char.inventory.num_item(ingredient) >= quantity:
                    has = True
                else:
                    has = False
                    can_make = False
                ingredients_list.append((ingredient, quantity, has))
            
            products_list = []
            for product in recipe.products.all():
                info = product.recipeproductinfo_set.get(recipe=recipe)
                quantity = info.quantity
                products_list.append((product, quantity))
            
            #Check if you have inventory space for products
            if can_make:
                alt = [(item, num) for (item, num, has) in ingredients_list]
                can_make = char.inventory.change_items(False, products_list, alt)
            
            known_recipes.append((recipe, ingredients_list, products_list,
                                  can_make))
        
        if char.inventory_mode==char.INV_FULL_ACCESS:
            making_allowed = True
        else:
            making_allowed = False
        
        data = {
            'known_recipes': known_recipes,
            'making_allowed': making_allowed #Edit/View Inventory mode 
        }
        return render(request, "game/global/crafting.html", data)
    else:
        ret = create_error(char, 'You are not allowed to make potions', 5)
        if ret:
            return ret
        else:
            return redirect(game_error)

#---Game Views

def v_generic_fight(request, char):
    monster = char.fight
    data = {
        "fight": monster
    }
    
    #Character damage to monster
    try:
        char_attack = char.get_gvp("char_attack")
        data["char_attack"] = char_attack.value
    except models.GameViewProperty.DoesNotExist:
        pass
    
    #Monster damage to character
    try:
        mons_attack = char.get_gvp("mons_attack")
        data["mons_attack"] = mons_attack.value
    except models.GameViewProperty.DoesNotExist:
        pass
    
    return render(request, "game/generic/fight.html", data)

def v_generic_fight_runaway(request, char):
    data = {
        "fight": char.fight
    }
    return render(request, "game/generic/fight_runaway.html", data)

def v_generic_fight_win(request, char):
    data = {
        "fight": char.fight,
        "char_attack": char.get_gvp("char_attack").value
    }
    return render(request, "game/generic/fight_win.html", data)

def v_generic_fight_loot(request, char):
    data = {
        "fight": char.fight,
        "fight_info": char.fight.monster_info,
        "weapon": char.fight.monster_info.weapon,
        "is_weapon_looted": char.fight.looted_weapon,
        "armour": char.fight.monster_info.armour,
        "is_armour_looted": char.fight.looted_armour,
    }
    return render(request, "game/generic/fight_loot.html", data)


def v_generic_fight_lose(request, char):
    data = {
        "fight": char.fight,
        "char_attack": char.get_gvp("char_attack").value,
        "mons_attack": char.get_gvp("mons_attack").value
    }
    return render(request, "game/generic/fight_lose.html", data)

def v_generic_shopping(request, char):
    shop_name = char.get_gvp("shop_name")
    
    shop = models.Shop.objects.get(name=shop_name.value)
    data = {"shop": shop}
    return render(request, "game/generic/shop.html", data)

def v_generic_resurrected(request, char):
    return render(request, "game/generic/resurrected.html")

def v_village_in(request, char):
    return render(request, "game/village/village_in.html")


def v_village_explore_nothing(request, char):
    data = {"text_selection": char.get_gvp("text_selection").value}
    return render(request, "game/village/village_explore_nothing.html", data)


def v_village_found_gold(request, char):
    char_gvps = char.get_gvps()
    text_selection = int(char_gvps.get(name="text_selection").value)
    gold = int(char_gvps.get(name="gold").value)
    
    data = {
        "text_selection": text_selection,
        "gold": gold
    }
    return render(request, "game/village/village_found_gold.html", data)

def v_village_in_market(request, char):
    return render(request, "game/village/village_market.html")

#---View Registration

NI = "-NOT IMPLEMENTED-"
registered_views = {
    "generic-fighting": v_generic_fight,
    "generic-fight-runaway": v_generic_fight_runaway,
    "generic-fight-win": v_generic_fight_win,
    "generic-fight-loot": v_generic_fight_loot,
    "generic-fight-lose": v_generic_fight_lose,
    "generic-shopping": v_generic_shopping,
    "generic-resurrected": v_generic_resurrected,
    "village-in": v_village_in,
    "village-exploring": NI,
    "village-found-gold": v_village_found_gold,
    "village-found-monster": NI,
    "village-found-berry": NI,
    "village-explore-nothing": v_village_explore_nothing,
    "village-in-market": v_village_in_market,
}

@login_required
def game_view_resolver(request):
    char = get_char(request)
    game_view = char.game_view
    try:
        http_response = registered_views[game_view](request, char)
        if http_response != NI:
            return http_response
        else:
            msg = "This view (%s) is not implemented"%game_view
            redir = create_error(char, msg, 5)
            return redir
    except KeyError:
        #Need to convey error somehow, temporary:
        err="Unknown game-view: %s" % game_view
        redir = create_error(char, err, 5)
        return redir


#---Game Actions
"""
Note all game actions must:
    - Ensure the character game view and GVPs (Game View Properties) are
    appropriate
    - Do stuff
    - Delete old game view and GVPs if appropriate
    - Create new game view and GVPs if appropriate
      (Note by create new game view it merely means replace the string
      char.game_view)
    - Return none if no errors (automatically redirects to game_view_resolver)

If there are errors then:
    - Return redirect(...)
    (Do things to handle error as you see fit.
    eg. return redirect(game_error) or you may return None still)
"""

@login_required
def game_action_resolver(request):
    def NIA(request, char):
        """Temporary function to indicate the game action is not implemented."""
        msg = "This action (%s) is not implemented"%action_name
        redir = create_error(char, msg, 5)
        return redir
    
    registered_actions = {
        "generic-purchase-item": a_generic_purchase_item,
        "generic-leave-shop": a_generic_leave_shop,
        "generic-fight-attack": a_generic_fight_attack,
        "generic-fight-runaway": a_generic_fight_runaway,
        "generic-fight-return": a_generic_fight_return,
        "generic-fight-goto-loot": a_generic_fight_goto_loot,
        "generic-fight-loot-item": a_generic_fight_loot_item,
        "generic-resurrect": a_generic_resurrect,
        "generic-resurrected-return": a_generic_resurrected_return,
        "inventory-drop-item": a_inventory_drop_item,
        "inventory-item-action": a_inventory_item_action,
        "crafting-make": a_crafting_make,
        "village-explore": a_village_explore,
        "village-return": a_village_return,
        "village-return-from-found-gold": a_village_return_from_found_gold,
        "village-goto-general-shop": a_village_goto_general_shop,
        "village-goto-herb-shop": a_village_goto_herb_shop,
        "village-goto-market": a_village_goto_market,
        "village-leave-market": a_village_leave_market
    }
    
    char = get_char(request)
    #All data is passed in through post
    if request.method == "POST":
        #Resolve POST data into an action
        try:
            action_name = request.POST["action_name"]
        except IndexError:
            msg="Action POST data incorrect- no 'action_name' defined.\
                You shouldn't see this."
            redir = create_error(char, msg, 5)
            return redir
        
        #Do action
        char = get_char(request)
        try:
            the_action = registered_actions[action_name]
        except KeyError:
            #Need to display error somehow, temporary:
            err="Unknown game-action: '%s'" % action_name
            models.Message.objects.create(character=char, body=err)
            return redirect(game_error)
        
        ret = the_action(request, char)
        if ret == None:
            return redirect(game_view_resolver)
        else:
            return ret

    
    else: #NOT POST
        msg="All game actions done through POST.\
            You shouldn't see this error."
        redir = create_error(char, msg, 5)
        return redir
    

@view_required("generic-shopping")
@allowed_exit_views("generic-shopping")
def a_generic_purchase_item(request, char):
    """Purchase an item at any shop
    
    Requires POST information:
    - item-name=Name of item
    
    Requires GVPs:
    - shop_name=Name of shop
    """
    
    #Check GVPs first
    shop_name = char.get_gvp("shop_name").value
    try:
        shop = models.Shop.objects.get(name=shop_name)
    except models.Shop.DoesNotExist:
        err = "The shop you are trying to purchase from does not exist"
        redir = create_error(char, err, 5)
        return redir
    
    item_name = request.POST["item-name"]
    the_iii = shop.inventory.get_iiis().filter(item__name=item_name)[0]
    
    #To purchase an item:
    #1-Ensure player has the inventory space (check stack_size if needed)
    #2-Ensure player has enough money
    #3-Subtract money
    #4-Decrease item count from shop inventory (remove item if necessary)
    #5-Add item to player's inventory (+1 to existing stack preferred)
    
    #1:
    #Check if they already have a stack of that
    the_char_iii = None
    char_iiis = char.inventory.get_iiis().filter(item__name=item_name)
    for char_iii in char_iiis:
        if char_iii.item.is_unlimited_stack:
            the_char_iii = char_iii
            break
        elif char_iii.stack_size < char_iii.item.max_stack_size:
            the_char_iii = char_iii
            break
    else: #Did not break for
        #No stacks with enough space, new new slot.
        if not char.inventory.has_free_slot():
            err = "You do not have the inventory space to purchase %s.\
            You should not see this error."%item_name
            return create_error(char, err, 5)
    
    #2:
    item_cost = the_iii.item.prop_cost()
    if not isinstance(item_cost, int):
        err = "This item is not for sale apparently?!\
        You should not see this error."
        return create_error(char, err, 5)
    
    if char.gold < item_cost:
        err = "You do not have enough money to purchase this item\
        You should not see this error."
        return create_error(char, err, 5)
    
    #3:
    char.gold -= item_cost
    char.save()
    
    #4:
    if the_iii.stack_size == 1:
        the_iii.delete()
    else:
        the_iii.stack_size -= 1
        the_iii.save()
    
    #5:
    if the_char_iii: #Existing non-full stack
        the_char_iii.stack_size += 1
        the_char_iii.save()
    else:
        item_object = models.Item.objects.get(name=item_name)
        new_char_iii = models.InventoryItemInfo(
            inventory=char.inventory, item=item_object, stack_size=1)
        new_char_iii.save()


@view_required("generic-fighting")
@allowed_exit_views("generic-fighting", "generic-fight-win",
                    "generic-fight-lose")
def a_generic_fight_attack(request, char):
    """Attack the monster the player is currently fighting."""
    
    def calculate_dmg(attacker, defender):
        """Calculate the damage done by the attacker to the defender"""
        att_dmg_max = attacker.weapon.prop_damage()
        def_abs_max = defender.armour.prop_damage_absorbed()
        att_dmg = random.randint(0, att_dmg_max)
        def_abs = random.randint(0, def_abs_max)
        damage_done = max(att_dmg - def_abs, 0)
        return int(damage_done)
    
    #Procedure
    #1-Damage monster
    #2-Check if dead -> goto fight_looting
    #3-Damage Character
    #4-Check if dead -> goto fight_lose -> player_death
    
    #1-Damage to monster
    char_damage = calculate_dmg(char, char.fight.monster_info)
    
    try:
        char.get_gvp("char_attack").delete()
    except models.GameViewProperty.DoesNotExist:
        pass
    
    models.GameViewProperty.objects.create(
        char=char, name="char_attack", value=char_damage)
    
    char.fight.hp = max(0, char.fight.hp - char_damage)
    char.fight.save()
    
    #2-Is the monster dead now?
    if char.fight.hp == 0:
        char.game_view = "generic-fight-win"
        char.save()
    else:
        #3-Damage Character
        mons_damage = calculate_dmg(char.fight.monster_info, char)
        
        try:
            char.get_gvp("mons_attack").delete()
        except models.GameViewProperty.DoesNotExist:
            pass
        
        models.GameViewProperty.objects.create(
            char=char, name="mons_attack", value=mons_damage)
        
        char.hp = max(0, char.hp - mons_damage)
        char.save()
        
        #4-Is player dead?
        if char.hp == 0:
            char.game_view = "generic-fight-lose"
            char.save()
    


@view_required("generic-fighting")
@allowed_exit_views("generic-fight-runaway")
def a_generic_fight_runaway(request, char):
    """Try to run away from the monster"""
    char.game_view = "generic-fight-runaway"
    char.save()

@view_required("generic-fight-runaway", "generic-fight-loot")
@allowed_exit_views("*")
def a_generic_fight_return(request, char):
    """Return to before the fight view specified by GVP:return_loc
    
    This is a generic way to leave a fight cleanly at any stage."""
    return_loc = char.get_gvp("return_loc")
    
    char.end_fight()
    char.game_view = return_loc.value
    char.save()
    
    return_loc.delete()
    
    if char.fight != None:
        active_monster = char.fight #Potentially destroys char by cascade
        char.fight = None           #When deleting the monster
        char.save()
        active_monster.delete() 
    
    #Delete various infos    
    try:
        char.get_gvp("char_attack").delete()
    except models.GameViewProperty.DoesNotExist:
        pass
    try:
        char.get_gvp("mons_attack").delete()
    except models.GameViewProperty.DoesNotExist:
        pass

@view_required("generic-fight-win")
@allowed_exit_views("generic-fight-loot")
def a_generic_fight_goto_loot(request, char):
    char.game_view = "generic-fight-loot"
    char.save()


@view_required("generic-fight-loot")
@allowed_exit_views("generic-fight-loot")
def a_generic_fight_loot_item(request, char):
    """Loot an item from the monster
    
    POST:
        -loot_type: weapon/armour/weapon-replace/armour-replace
    """
    
    loot_type = request.POST["type"]
    
    if loot_type in ("weapon", "weapon-replace"):
        if char.fight.looted_weapon:
            err = "Major Error: You have already looted the weapon."
            return create_error(char, err, 5)
        elif char.fight.monster_info.weapon.is_soulbound:
            err = "Major Error: The weapon is soulbound, you cannot loot it."
            return create_error(char, err, 5)
        elif loot_type == "weapon":
            weapon = char.fight.monster_info.weapon
            if char.inventory.is_space_for_item(weapon, 1):
                char.inventory.add_item(weapon, 1)
                char.fight.looted_weapon = True
                char.fight.save()
            else:
                err = "You do not have enough inventory space to loot that."
                return create_error(char, err, 0)
        elif loot_type == "weapon-replace":
            weapon = char.fight.monster_info.weapon
            char.weapon = weapon
            char.fight.looted_weapon = True
            char.save()
            char.fight.save()
    elif loot_type in ("armour", "armour-replace"):
        if char.fight.looted_armour:
            err = "Major Error: You have already looted the armour."
            return create_error(char, err, 5)
        elif char.fight.monster_info.armour.is_soulbound:
            err = "Major Error: The armour is soulbound, you cannot loot it."
            return create_error(char, err, 5)
        elif loot_type == "armour":
            armour = char.fight.monster_info.armour
            if char.inventory.is_space_for_item(armour, 1):
                char.inventory.add_item(armour, 1)
                char.fight.looted_armour = True
                char.fight.save()
            else:
                err = "You do not have enough inventory space to loot that."
                create_error(char, err, 0)
        elif loot_type == "armour-replace":
            armour = char.fight.monster_info.armour
            char.armour = armour
            char.fight.looted_armour = True
            char.save()
            char.fight.save()
    else:
        err = "Major Error: You can only loot a weapon or an armour."
        return create_error(char, err, 5)
    


@view_required("generic-shopping")
@allowed_exit_views("*")
def a_generic_leave_shop(request, char):
    """Leave the current shop
    
    Requires GVPs:
    - return_location=Name of view to return to
    """
    
    return_loc = char.get_gvp("return_location")
    
    for gvp in char.get_gvps().all():
        gvp.delete()
    
    char.game_view = return_loc.value
    char.save()


@view_required("generic-fight-lose")
@allowed_exit_views("generic-resurrected")
def a_generic_resurrect(request, char):
    """Bring the character back to life
    Requires GVPs:
    - return_location=Name of view to return to"""
    char.resurrect()
    
    #Delete all GVPs except the return_loc
    char.gameviewproperty_set.exclude(name="return_loc").delete()
    
    char.game_view = "generic-resurrected"
    char.save()
    
@view_required("generic-resurrected")
@allowed_exit_views("*")
def a_generic_resurrected_return(request, char):
    """Return to the return_loc after resurrection
    Requires GVPs:
    - return_location=Name of view to return to"""
    return_loc_gvp = char.get_gvp("return_loc")
    char.game_view = return_loc_gvp.value
    char.save()
    return_loc_gvp.delete()


@view_required("*")
@allowed_exit_views("*")
def a_inventory_drop_item(request, char):
    """Drop an item from the inventory
    
    Requires POST:
        item-name: the item name
        amount: number/"all"
    """
    
    if char.inventory_mode != char.INV_FULL_ACCESS:
        err = "Major error: Cannot drop item without full inventory access"
        ret = create_error(char, err, 5)
        if ret:
            return ret
    
    item_name = request.POST["item-name"]
    amount = request.POST["amount"]
    
    try:
        item = models.Item.objects.get(name=item_name)
    except models.Item.DoesNotExist:
        err = "Major error: Dropping item,"+\
        "Item not in inventory- you should not see this"
        return create_error(char, err, 5)
    
    if amount == "all":
        pass_amount = char.inventory.num_item(item)
    else:
        try:
            pass_amount = int(amount)
        except ValueError:
            err = "Major error: Dropping item, amount not specified properly"+\
            " amount({0})".format(amount)
            return create_error(char, err, 5)
    
    char.inventory.remove_item(item, pass_amount)
    
    return redirect(char_inventory)

@view_required("*")
@allowed_exit_views("*")
def a_inventory_item_action(request, char):
    """Do an item action from the inventory
    
    Requires POST:
        item-name: the item name
        action-name: name of action"
    """
    
    if char.inventory_mode != char.INV_FULL_ACCESS:
        err = "Major error: Cannot do an item action without full inventory access"
        ret = create_error(char, err, 5)
        if ret:
            return ret
    
    item_name = request.POST["item-name"]
    action_name = request.POST["action-name"]
    
    try: #Ensure we have the item
        item = models.Item.objects.get(name=item_name)
    except models.Item.DoesNotExist:
        err = "Major error: Item action, "+\
        "Item not in inventory - you should not be seeing this error."
        create_error(char, err, 5)
    
    action_list = item.get_named_props("action")
    if action_list:
        for action in action_list:
            if action.value == action_name:
                item_actions.do_action(action_name, char, item)
                return redirect(char_inventory)
    
    #No action_list or no corresponding action
    err = "Major error: Item action, "+\
    "The item does not have that action - you should not be seeing this error."
    ret = create_error(char, err, 5)
    if ret is not None:
        return ret
    
    return redirect(char_inventory)


@view_required('*')
@allowed_exit_views('*')
def a_crafting_make(request, char):
    """Make an item
    
    Requires POST:
        recipe-name: Name of recipe that is being used
    """
    
    recipe_name = request.POST['recipe-name']
    
    try:
        recipe = models.Recipe.objects.get(name=recipe_name)
    except models.Recipe.DoesNotExist:
        return create_error(char, 'Unknown recipe: {}'.format(recipe_name), 5)
    
    #Check you have ingredients
    has_ingredients = True
    ingredients_list = []
    for ingredient in recipe.ingredients.all():
        info = ingredient.recipeingredientinfo_set.get(recipe=recipe)
        num = info.quantity
        ingredients_list.append((ingredient, num))
        if char.inventory.num_item(ingredient) < num:
            has_ingredients = False
            break
    
    #Check you will have the inventory space for products
    if has_ingredients:
        products_list = recipe.products_list()
        print(products_list)
        try:
            char.inventory.change_items(True, products_list, ingredients_list)
        except models.InventoryLacksSpace:
            create_error(char, "Not enough inventory space", 5)
        else:
            msg = "Made {} using {}"
            msg = msg.format(products_list, ingredients_list)
            create_msg(char, msg)
    
    return redirect(crafting)
    

@view_required("village-in", "village-explore-nothing", "village-in-market")
@allowed_exit_views("village-found-gold", "village-explore-nothing",
                    "generic-fighting")
def a_village_explore(request, char):
    
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
    return create_error(char, err, 10)


@view_required("village-explore-nothing")
@allowed_exit_views("village-in")
def a_village_return(request, char):
    char.game_view = "village-in"
    char.save()
    
    for gvp in char.get_gvps().all():
        gvp.delete()


@view_required("village-found-gold")
@allowed_exit_views("village-in")
def a_village_return_from_found_gold(request, char):
    char.game_view = "village-in"
    char.save()
    
    for gvp in char.get_gvps().all():
        gvp.delete()


@view_required("village-in-market")
@allowed_exit_views("generic-shopping")
def a_village_goto_general_shop(request, char):
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

@view_required("village-in-market")
@allowed_exit_views("generic-shopping")
def a_village_goto_herb_shop(request, char):
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


@view_required("village-in")
@allowed_exit_views("village-in-market")
def a_village_goto_market(request, char):
    char.game_view = "village-in-market"
    char.save()

@view_required("village-in-market")
@allowed_exit_views("village-in")
def a_village_leave_market(request, char):
    char.game_view = "village-in"
    char.save()


@login_required
def introduction(request):
    return render_to_response("game/introduction.html",
                              context_instance=RequestContext(request))


#---Other

@login_required
def delete_message(request, msg_num):
    """Delete the message specified"""
    char = get_char(request)
    msg_num = int(msg_num)
    
    next_page = request.POST["next_page"]
    
    try:
        models.Message.objects.filter(character=char)[msg_num].delete()
    except IndexError:
        err="Message does not exist to delete."
        models.Message.objects.create(character=char, body=err)
    return redirect(next_page)


@login_required
def game_error(request):
    """Generic error page"""
    char = get_char(request)
    data = {}
    if len(char.message_set.all()):
        return render_to_response("game/error.html", data,
                                  context_instance=RequestContext(request))
    else:
        return redirect(introduction)
