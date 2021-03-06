'''
This handles all actions for items in the inventory.
The action could do anything.
The action may return a string. (TODO: Why?)
The action may also create Message objects for the player.

Action functions require the item and the target.
The target must be a Character (for now).
'''

def ia_self_heal_once(char, item, target):
    """Heal the target and destroy the item
    
    Uses the property "health healed"
    """
    
    #Models must be here to avoid global conflicts with django.models
    import game.models as models
    
    if target.hp != target.max_hp:
        heal = item.prop_health_healed
        target.hp = min(target.max_hp, target.hp + heal)
        target.save()
        char.inventory.remove_item(item)
        
        msg = "You healed upto {} HP.".format(heal)
        models.Message.objects.create(character=char, body=msg)
    else:
        err = "You are already at full hp."
        models.Message.objects.create(character=char, body=err)
        return err


def ia_damage_once(char, item, target):
    """Damage the target and destroy the item
    
    **This does NOT handle what happens to the target when at 0hp**
    
    Uses the property "damage"
    """
    
    target.hp = max(0, target.hp - item.prop_damage)
    target.save()
    char.inventory.remove_item(item)


def get_item_action_choices():
    for f in ITEM_ACTIONS.keys():
        yield (f,f)


ITEM_ACTIONS = {
    "self heal; one use": ia_self_heal_once,
    "damage target; one use": ia_damage_once
}
