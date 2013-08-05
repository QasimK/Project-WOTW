'''
Created on 5 Aug 2013

@author: Qasim
'''

from django.shortcuts import redirect

from wotw_project.game import models, item_actions
from wotw_project.game.views import ActionError, char_inventory

#@view_required("*")
#@allowed_exit_views("*")
def inventory_item_action(char, post):
    """Do an item action from the inventory
    
    Requires POST:
        item-name: the item name
        action-name: name of action"
    """
    
    if char.inventory_mode != char.INV_FULL_ACCESS:
        err = "Major error: Cannot do an item action without full inventory access"
        raise ActionError(err)
    
    item_name = post["item-name"]
    action_name = post["action-name"]
    
    try: #Ensure we have the item
        item = models.Item.objects.get(name=item_name)
    except models.Item.DoesNotExist:
        err = "Major error: Item action, "+\
        "Item not in inventory - you should not be seeing this error."
        raise ActionError(err)
    
    assert isinstance(item, models.Item)
    
    action_list = item.get_item_actions()
    the_item_action = None
    for item_action, display_text in action_list:
        if item_action.func == action_name:
            the_item_action = item_action
            assert isinstance(the_item_action, models.ItemAction)
            break
    
    if the_item_action:
        if char.fight is None and not the_item_action.allow_out_combat:
            err = "Major error: Cannot use item out of combat"
            raise ActionError(err)
        elif char.fight is not None and not the_item_action.allow_in_combat:
            err = "Major error: Cannot use item in of combat"
            raise ActionError(err)
        else:
            action_func = item_actions.ITEM_ACTIONS[action_name]
            
            if item_action.target == item_action.TAR_CHAR:
                action_func(char, item, char)
            elif item_action.target == item_action.TAR_FIGHT:
                pass
            elif item_action.target == item_action.TAR_INV_ITEM:
                pass
            
            return redirect(char_inventory)
    
    #No action_list or no corresponding action
    err = "Major error: Item action, "+\
    "The item does not have that action - you should not be seeing this error."
    raise ActionError(err)


#@view_required("*")
#@allowed_exit_views("*")
def inventory_drop_item(char, post):
    """Drop an item from the inventory
    
    Requires POST:
        item-name: the item name
        amount: number/"all"
    """
    
    if char.inventory_mode != char.INV_FULL_ACCESS:
        err = "Major error: Cannot drop item without full inventory access"
        raise ActionError(err)
    
    item_name = post["item-name"]
    amount = post["amount"]
    
    try:
        item = models.Item.objects.get(name=item_name)
    except models.Item.DoesNotExist:
        err = "Major error: Dropping item,"+\
        "Item not in inventory- you should not see this"
        raise ActionError(err)
    
    if amount == "all":
        pass_amount = char.inventory.num_item(item)
    else:
        try:
            pass_amount = int(amount)
        except ValueError:
            err = "Major error: Dropping item, amount not specified properly"+\
            " amount({0})".format(amount)
            raise ActionError(err)
    
    char.inventory.remove_item(item, pass_amount)
    
    return redirect(char_inventory)
