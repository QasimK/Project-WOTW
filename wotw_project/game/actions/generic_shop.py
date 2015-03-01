'''
Created on 5 Aug 2013

@author: Qasim
'''

from game import models

#@view_required("generic-shopping")
#@allowed_exit_views("generic-shopping")
def generic_shop_purchase(char, post):
    """Purchase an item at any shop
    
    Requires POST information:
    - item-name=Name of item
    
    Requires GVPs:
    - shop_name=Name of shop
    """
    
    from game.views import ActionError
    
    #Check GVPs first
    shop_name = char.get_gvp("shop_name").value
    try:
        shop = models.Shop.objects.get(name=shop_name)
    except models.Shop.DoesNotExist:
        err = "The shop you are trying to purchase from does not exist"
        raise ActionError(err)
    
    item_name = post["item-name"]
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
            raise ActionError(err)
    
    #2:
    item_cost = the_iii.item.prop_cost
    if not isinstance(item_cost, int):
        err = "This item is not for sale apparently?!\
        You should not see this error."
        raise ActionError(err)
    
    if char.gold < item_cost:
        err = "You do not have enough money to purchase this item\
        You should not see this error."
        raise ActionError(err)
    
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


#@view_required("generic-shopping")
#@allowed_exit_views("*")
def generic_shop_leave(char, post):
    """Leave the current shop
    
    Requires GVPs:
    - return_location=Name of view to return to
    """
    
    return_loc = char.get_gvp("return_location")
    
    for gvp in char.get_gvps().all():
        gvp.delete()
    
    char.game_view = return_loc.value
    char.save()
