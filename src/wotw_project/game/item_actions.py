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

class ItemAction:
    """Don't create these objects"""
    allow_character_target = False
    allow_fight_target = False
    #allow_environment_target = False
    allow_in_combat = False
    allow_out_combat = False
    
    def __new__(self):
        raise NotImplementedError
    
    @classmethod
    def __do__(cls, char, item, target):
        raise NotImplementedError


class IASelfHealOnce(ItemAction):
    """Heal the target and destroy the item
    
    Uses the property "health healed"
    """
    
    allow_character_target = True
    allow_in_combat = True                                
    allow_out_combat = True
    
    @classmethod
    def __do__(cls, char, item, target):
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
    "self heal; one use": IASelfHealOnce
}