'''
Created on 9 Apr 2011

@author: Qasim

This handles all actions for items in the inventory.
The action may return a string.
The action may also create Message objects for the player.
The action could do anything.

Action functions require the item and the target.
The target must be a Character (for now).
'''

from wotw_project.game import models


def ia_self_heal_once(char, item, target):
    """Heal the target and destroy the item
    
    Uses the property "health healed"
    """
    
    if target.hp != target.max_hp:
        heal = item.prop_health_healed()
        target.hp = min(target.max_hp, target.hp + heal)
        target.save()
        target.inventory.remove_item(item)
        
        msg = "You healed upto {} HP.".format(heal)
        models.Message.objects.create(character=char, body=msg)
    else:
        err = "You are already at full hp."
        models.Message.objects.create(character=char, body=err)
        return err


ITEM_ACTIONS = {
    "self heal; one use": ia_self_heal_once
}
