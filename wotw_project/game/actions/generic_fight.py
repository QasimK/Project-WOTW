import random

from game import models

##@view_required("generic-fighting")
##@allowed_exit_views("generic-fighting", "generic-fight-win",
#                    "generic-fight-lose")
def generic_fight_attack(char, post):
    """Attack the monster the player is currently fighting."""
    
    def calculate_dmg(attacker, defender):
        """Calculate the damage done by the attacker to the defender"""
        att_dmg_max = attacker.weapon.prop_damage
        def_abs_max = defender.armour.prop_damage_absorbed
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
    


#@view_required("generic-fighting")
#@allowed_exit_views("generic-fight-runaway")
def generic_fight_runaway(char, post):
    """Try to run away from the monster"""
    char.game_view = "generic-fight-runaway"
    char.save()

#@view_required("generic-fight-runaway", "generic-fight-loot")
#@allowed_exit_views("*")
def generic_fight_return(char, post):
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

#@view_required("generic-fight-win")
#@allowed_exit_views("generic-fight-loot")
def generic_fight_goto_loot(char, post):
    char.game_view = "generic-fight-loot"
    char.save()


#@view_required("generic-fight-loot")
#@allowed_exit_views("generic-fight-loot")
def generic_fight_loot_item(char, post):
    """Loot an item from the monster
    
    POST:
        -loot_type: weapon/armour/weapon-replace/armour-replace
    """
    
    loot_type = post["type"]
    
    from game.views import ActionError
    
    if loot_type in ("weapon", "weapon-replace"):
        if char.fight.looted_weapon:
            err = "Major Error: You have already looted the weapon."
            raise ActionError(err)
        elif char.fight.monster_info.weapon.is_soulbound:
            err = "Major Error: The weapon is soulbound, you cannot loot it."
            raise ActionError(err) 
        elif loot_type == "weapon":
            weapon = char.fight.monster_info.weapon
            if char.inventory.is_space_for_item(weapon, 1):
                char.inventory.add_item(weapon, 1)
                char.fight.looted_weapon = True
                char.fight.save()
            else:
                err = "You do not have enough inventory space to loot that."
                raise ActionError(err)
        elif loot_type == "weapon-replace":
            weapon = char.fight.monster_info.weapon
            char.weapon = weapon
            char.fight.looted_weapon = True
            char.save()
            char.fight.save()
    elif loot_type in ("armour", "armour-replace"):
        if char.fight.looted_armour:
            err = "Major Error: You have already looted the armour."
            raise ActionError(err)
        elif char.fight.monster_info.armour.is_soulbound:
            err = "Major Error: The armour is soulbound, you cannot loot it."
            raise ActionError(err)
        elif loot_type == "armour":
            armour = char.fight.monster_info.armour
            if char.inventory.is_space_for_item(armour, 1):
                char.inventory.add_item(armour, 1)
                char.fight.looted_armour = True
                char.fight.save()
            else:
                err = "You do not have enough inventory space to loot that."
                raise ActionError(err)
        elif loot_type == "armour-replace":
            armour = char.fight.monster_info.armour
            char.armour = armour
            char.fight.looted_armour = True
            char.save()
            char.fight.save()
    else:
        err = "Major Error: You can only loot a weapon or an armour."
        raise ActionError(err)
