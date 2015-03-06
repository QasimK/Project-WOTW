from functools import wraps

from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

import game.models as models
import game.actions as a

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
    return models.Character.objects.get(user_account=request.user)

def create_msg(char, msg):
    """Just a message"""
    models.Message.objects.create(character=char, body=msg)

class ActionError(Exception):
    """An action which should not have been an option occurred
    
    Either the user was poking around or I messed up"""
    
    def __init__(self, err):
        self.err = err
    
    def __str__(self):
        return self.err

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


#Decorator
def view_required(*views):
    """Specify that specific game-views (given as strings) are required
    for the character for this ACTION to be valid."""
    
    for view in views:
        if view != "*" and view not in registered_views.keys():
            raise IncorrectViewName(view)
    
    def wrap_func(func):
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


#---Global Views

@login_required
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


@login_required
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
            msg = "This view (%s) is not implemented" % game_view
            redir = create_error(char, msg, 5)
            return redir
    except KeyError:
        err="Unknown game-view: %s" % game_view
        redir = create_error(char, err, 5)
        return redir


#---Game Actions
"""
Note all game a must:
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
    """Resolve game actions
    
    Data passed in through POST:
    - action_name
    - Whatever other variables are used by the action"""
    
    def NIA(request, char):
        """Temporary function to indicate the game action is not implemented."""
        msg = "This action (%s) is not implemented"%action_name
        models.Message.objects.create(character=char, body=msg)
        return redirect(game_error)
    
    registered_actions = {
        "generic-purchase-item": a.generic_shop_purchase,
        "generic-leave-shop": a.generic_shop_leave,
        "generic-fight-attack": a.generic_fight_attack,
        "generic-fight-runaway": a.generic_fight_runaway,
        "generic-fight-return": a.generic_fight_return,
        "generic-fight-goto-loot": a.generic_fight_goto_loot,
        "generic-fight-loot-item": a.generic_fight_loot_item,
        "generic-resurrect": a_generic_resurrect,
        "generic-resurrected-return": a_generic_resurrected_return,
        "inventory-drop-item": a.inventory_drop_item,
        "inventory-item-action": a.inventory_item_action,
        "crafting-make": a_crafting_make,
        "village-explore": a.village_explore,
        "village-return": a.village_return,
        "village-return-from-found-gold": a.village_return_from_found_gold,
        "village-goto-general-shop": a.village_goto_general_shop,
        "village-goto-herb-shop": a.village_goto_herb_shop,
        "village-goto-market": a.village_goto_market,
        "village-leave-market": a.village_leave_market
    }
    
    char = get_char(request)
    #Resolve POST data into an action
    try:
        action_name = request.POST["action_name"]
    except IndexError:
        msg="Action POST data incorrect- no 'action_name' defined.\
            You shouldn't see this."
        redir = create_error(char, msg, 5)
        return redir
    
    #Get action
    try:
        the_action = registered_actions[action_name]
    except KeyError:
        #Need to display error somehow, temporary:
        err="Unknown game-action: '{}'".format(action_name)
        models.Message.objects.create(character=char, body=err)
        return redirect(game_error)
    
    #Do action
    try:
        ret = the_action(char, request.POST)
    except ActionError as error:
        models.Message.objects.create(character=char, body=str(error))
        return redirect(game_error)
    
    if ret is None:
        return redirect(game_view_resolver)
    else:
        return ret


#@view_required("generic-fight-lose")
#@allowed_exit_views("generic-resurrected")
def a_generic_resurrect(char, post):
    """Bring the character back to life
    Requires GVPs:
    - return_location=Name of view to return to"""
    char.resurrect()
    
    #Delete all GVPs except the return_loc
    char.gameviewproperty_set.exclude(name="return_loc").delete()
    
    char.game_view = "generic-resurrected"
    char.save()
    
#@view_required("generic-resurrected")
#@allowed_exit_views("*")
def a_generic_resurrected_return(char, post):
    """Return to the return_loc after resurrection
    Requires GVPs:
    - return_location=Name of view to return to"""
    return_loc_gvp = char.get_gvp("return_loc")
    char.game_view = return_loc_gvp.value
    char.save()
    return_loc_gvp.delete()


#@view_required('*')
#@allowed_exit_views('*')
def a_crafting_make(char, post):
    """Make an item
    
    Requires POST:
        recipe-name: Name of recipe that is being used
    """
    
    recipe_name = post['recipe-name']
    
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
