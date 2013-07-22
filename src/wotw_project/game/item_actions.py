'''
Created on 9 Apr 2011

@author: Qasim

This handles all actions for items in the inventory.
The action may return a string.
The action may also create Message objects for the player.
The action could do anything.

Action functions require the item and the target.
The target must be a Character (for now).

All subject to change. Obviously.
'''

from wotw_project.game import models

def ia_heal(item, target):
    """Heal the target and destroy the item
    Property: health healed"""
    if target.hp != target.max_hp:
        heal = item.prop_health_healed()
        target.hp = min(target.max_hp, target.hp + heal)
        target.save()
        target.inventory.remove_item(item)
        
        msg = "You ate the whatever and healed upto {} HP.".format(heal)
        models.Message.objects.create(target=target, body=msg)
    else:
        err = "You are already at full hp."
        models.Message.objects.create(target=target, body=err)
        return err


ITEM_ACTIONS = {
    "heal": ia_heal
}