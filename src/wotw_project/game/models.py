#Currently broken: Item actions.
import random

from django.db import models, transaction
from django.db.models import Q
from django.contrib.auth import models as models_auth
from django.db.models.signals import post_delete
from django.dispatch import receiver

#---Exceptions
class WotwGameException(RuntimeError):
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return self.s

class PlayerAlreadyFighting(WotwGameException):
    def __init__(self, char_fight):
        self.char_fight = char_fight
    def __str__(self):
        return "The player is already fighting with a monster: %s"%\
                self.char_fight


class InventoryDoesNotHaveItem(WotwGameException):
    """The inventory from which the items were being removed does not have
    that item"""
    def __init__(self, inventory, item):
        self.inventory = inventory
        self.item = item
    def __str__(self):
        err = "The inventory %s does not have any items %s"%(
            self.inventory, self.item.name)
        return err

class InventoryDoesNotHaveEnoughItems(WotwGameException):
    """The inventory specified does not have enough of a certain item"""
    def __init__(self, inventory, item, amount_required):
        self.inventory = inventory
        self.item = item
        self.amount_required = amount_required
    def __str__(self):
        err = "The inventory %s does not have enough of the item: %s. "+\
            "%s item(s) are required."%(self.inventory, self.item.name,
                self.amount_required)
        return err

class InventoryIsUnlimited(WotwGameException):
    """The inventory is unlimited and does not have a size"""
    def __init__(self, inventory):
        self.inventory = inventory
    def __str__(self):
        err = "The inventory %s is unlimited and therefore does not have a size"%\
            self.inventory
        return err

class ItemIsUnlimitedStack(WotwGameException):
    """The item has an unlimited stack size
    Therefore there is no concept of stack space still free."""
    def __init__(self, item):
        self.item
    def __str__(self):
        err = "The item %s has an unlimited stack size tehrefore does not have\
        a stack space left number"%self.item.name
        return err


class InventoryLacksSpace(WotwGameException):
    def __init__(self, inventory, item=None, amount=None):
        self.inventory = inventory
        self.item = item
        self.amount = amount
    def __str__(self):
        err = "There is not enough space in the inventory ({0})"\
                .format(self.inventory)
        if self.item:
            err += "\nItem: {1}".format(self.item)
        else:
            err = "There is not enough space in the inventory ({0})"\
                    .format(self.inventory)
        return err



#---Models
class Character(models.Model):
    INV_FULL_ACCESS = 'A'
    INV_VIEW_ONLY = 'B'
    INV_NO_ACCESS = 'C'
    INVENTORY_MODE_CHOICES = ((INV_FULL_ACCESS, 'Edit/View'),
                              (INV_VIEW_ONLY, 'View-only'),
                              (INV_NO_ACCESS, 'No access'))
    
    user_account = models.ForeignKey(models_auth.User)
    max_hp = models.IntegerField(default=50)
    hp = models.IntegerField(default=50)
    
    #This inventory is created on char creation. Special Deletion code required.
    inventory = models.OneToOneField('Inventory')
    inventory_mode = models.CharField(max_length=1,
                                      choices=INVENTORY_MODE_CHOICES,
                                      default=INV_FULL_ACCESS)
    
    weapon = models.ForeignKey('Item', related_name="character_weapon")
    armour = models.ForeignKey('Item', related_name="character_armour")
    gold = models.IntegerField(default=300)
    
    #Special Delete code required for this
    fight = models.OneToOneField('ActiveMonster', blank=True, null=True)
    
    game_view = models.CharField(max_length=100, default="village-in")
    
    #These are created when character is created
    known_recipes = models.ManyToManyField('Recipe')
    
    def __unicode__(self):
        return self.user_account.__unicode__()
    
    @classmethod
    def make_new_character(cls, user_account):
        """Create and return a new character"""
        inv = Inventory.objects.create(is_unlimited=False, size=12)
        weapon = Item.objects.get(name="Fists and Legs")
        armour = Item.objects.get(name="Clothes")
        char = cls.objects.create(user_account=user_account, inventory=inv,
                                  weapon=weapon, armour=armour)
        
        default_recipes = Recipe.objects.filter(
            Q(name__iexact='Waking Brew Recipe') |
            Q(name__iexact='Wounds Potion Recipe') |
            Q(name__iexact='Nightshade Potion Recipe') |
            Q(name__iexact='Rock Concoction Recipe') |
            Q(name__iexact='Sleeping Brew Recipe')).values_list('pk', flat=True)
        assert len(default_recipes) == 5
        char.known_recipes.add(*default_recipes)
        return char
    
    def resurrect(self):
        """Reset the character as though it has died.
        
        You must handle any GVPs and the location of the character."""
        
        self.hp = self.max_hp
        self.gold = int(self.gold / 2)
        
        active_monster = self.fight
        self.fight = None
        self.save()
        
        if active_monster != None:
            active_monster.delete()
    
    
    def get_gvps(self):
        """Return all game view properties regardless of whether they were
        meant for this view or not.
        
        If they were not meant for this view then someone may have forgotten
        to delete the property."""
        
        return self.gameviewproperty_set
    
    def get_gvp(self, gvp_name):
        """Return the specfied GVP"""
        return self.gameviewproperty_set.get(name=gvp_name)
    
    def start_fight(self, monster):
        """Start a fight with the specified monster doing all backend work.
        
        'monster' argument can be the name of the monster or the pk.
        
        Warning: Does not see if context of fight is valid.
        (ie. are you allowed to start a fight right now?)"""
        
        if self.fight != None:
            raise PlayerAlreadyFighting(self.fight)
        
        if isinstance(monster, (int, long) ):
            monster_info = Monster.objects.get(pk=monster)
        else:
            monster_info = Monster.objects.get(name=monster)
        
        gold = int(random.normalvariate(monster_info.gold, monster_info.gold_dev))
        hp = int(random.normalvariate(monster_info.hp, monster_info.hp_dev))
        
        active_monster = ActiveMonster(monster_info=monster_info,
            hp=hp, gold=gold)
        active_monster.save()
        
        self.fight = active_monster
        self.inventory_mode = self.INV_VIEW_ONLY
        self.save()
    
    def end_fight(self):
        """End the fight"""
        self.inventory_mode = self.INV_FULL_ACCESS
        self.save()


@receiver(post_delete, sender=Character, dispatch_uid='gam_cha_predelet')
def character_delete(sender, instance, **kwargs):
    character = instance
    try:
        character.inventory.delete()
    except Inventory.DoesNotExist:
        pass
    if character.fight:
        character.fight.delete()


class GameViewProperty(models.Model):
    """Additional game view info attached to the characters current view.
    
    Each game view property is informal, there is currently
    no list of game view properties (GVPs).
    
    These properties should be deleted as appropriate when the
    game-view changes for the character. This is important because
    if GVPs are not deleted, they will simply build up and may have unintended
    consequences."""
    
    char = models.ForeignKey(Character)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "game view property"
        verbose_name_plural = "game view properties"
        unique_together = ("char", "name")
    
    def __unicode__(self):
        return "GVP(char: %s, name: %s, value: %s)"%\
            (self.char, self.name, self.value)
        




class Monster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    hp = models.IntegerField()
    hp_dev = models.IntegerField(default=0)
    
    weapon = models.ForeignKey('Item', related_name="monster_weapons")
    armour = models.ForeignKey('Item', related_name="monster_armours")
    
    gold = models.IntegerField(default=0)
    gold_dev = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name


def create_activemonster_from_info(monster_info):
    """Create ActiveMoster object from monster info
    monster_info = Monster object from database"""
    gold = int(random.normalvariate(monster_info.gold, monster_info.gold_dev))
    
    return ActiveMonster.objects.create(monster_info=monster_info,
        hp=monster_info.max_hp, weapon=monster_info.weapon,
        armour=monster_info.armour, gold=gold)


class ActiveMonster(models.Model):
    """A monster which is an 'instance' from the standard monster data.
    This is fighting the player"""
    
    monster_info = models.ForeignKey('Monster')
    hp = models.IntegerField()
    gold = models.IntegerField(default=0)
    
    #Probably still has fields 'weapon' and 'armour'
    #in the database file.
    looted_weapon = models.BooleanField(default=False)
    looted_armour = models.BooleanField(default=False)
    
    def __unicode__(self):
        return str(self.monster_info)



class Item(models.Model):
    """All items must have a unique name, a cost and the max. stack size.
    (is_unlimited_stack = True means it can stack forever
    otherwise set a max_stack_size)
    
    Shops ignore the stack size. Stack size is used for player inventories.
    Shops use the cost.
    
    Also use objects=ItemManager() on subclasses"""
    name = models.CharField(max_length=100, unique=True)
    
    is_unlimited_stack = models.BooleanField(default=False)
    max_stack_size = models.PositiveIntegerField(default=1)
    
    is_soulbound = models.BooleanField(default=False)
    
    item_actions = models.ManyToManyField('ItemAction')
    
    @property
    def prop_damage(self):
        """Return the damage item property"""
        return int(self.itemproperty_set.get(name=ItemProperty.DAMAGE).value)
    
    @property
    def prop_damage_absorbed(self):
        """Return the damage absorbed item property"""
        prop = self.itemproperty_set.get(name=ItemProperty.DAMAGE_ABSORBED)
        return int(prop.value)
    
    @property
    def prop_cost(self):
        prop = self.itemproperty_set.get(name=ItemProperty.COST)
        return int(prop.value)
    
    @property
    def prop_health_healed(self):
        prop = self.itemproperty_set.get(name=ItemProperty.HEALTH_HEALED)
        return int(prop.value)
    
    
    #===========================================================================
    # #Property stuff
    # def get_all_ipis(self):
    #    """Return all IPIs for this object"""
    #    return self.itempropertyinfo_set.all()
    # 
    # 
    # def get_all_props_ext(self):
    #    """Return a list of (item property name, item property info object)"""
    #    ps = []
    #    #itempropertyinfo
    #    for ipi in self.itempropertyinfo_set.all():
    #        ps.append( (ipi.item_property.name, ipi) )
    #    return ps
    # 
    # def get_all_props(self):
    #    """Return all IPIs"""
    #    return self.itempropertyinfo_set.all()
    # 
    # def get_named_props(self, prop_name):
    #    """Return the list of item properties with the name specified"""
    #    ipis = self.itempropertyinfo_set.filter(item_property__name=prop_name)
    #    if ipis:
    #        return ipis
    #    return None
    # 
    # def get_named_prop(self, prop_name):
    #    """Return the *single* item property *value* specified
    #    
    #    Need to check this:
    #    If there is more than one it will return the first one."""
    #    try:
    #        ipi = self.itempropertyinfo_set.get(item_property__name=prop_name)
    #        return ipi.value
    #    except ItemPropertyInfo.DoesNotExist:
    #        return None
    # 
    # 
    # def prop_damage(self):
    #    """Shortcut: Return damage property of item if there is one"""
    #    ret = self.get_named_prop("damage")
    #    if ret:
    #        return int(ret)
    # 
    # def prop_damage_absorbed(self):
    #    ret = self.get_named_prop("damage absorbed")
    #    if ret:
    #        return int(ret)
    # 
    # def prop_health_healed(self):
    #    ret = self.get_named_prop("health healed")
    #    if ret:
    #        return int(ret)
    # 
    # def prop_soulbound(self):
    #    ret = self.get_named_prop("soulbound")
    #    if ret in ("true",):
    #        return True
    #    elif ret in ("false",):
    #        return False
    #    elif not ret: #ret=None
    #        return False
    # 
    # def prop_cost(self):
    #    ret = self.get_named_prop("cost")
    #    if ret:
    #        return int(ret)
    # 
    #===========================================================================
    
    def __unicode__(self):
        return self.name




class ItemProperty(models.Model):
    """A property that exists on an item"""
    
    COST = 'cst'
    DAMAGE = "dmg"
    HEALTH_HEALED = "hh"
    DAMAGE_ABSORBED = "da"
    NAME_CHOICES = (
        (COST, "Cost"),
        (DAMAGE, "Damage Dealt"),
        (HEALTH_HEALED, "Health Healed"),
        (DAMAGE_ABSORBED, "Damage Absorbed"),
    )
    
    item = models.ForeignKey(Item)
    name = models.CharField(max_length=3, choices=NAME_CHOICES)
    value = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "item property"
        verbose_name_plural = "item properties"
        unique_together = ("item", "name", "value")
    
    def __unicode__(self):
        return self.name


def get_item_action_choices():
    from wotw_project.game import item_actions
    return [(f, f) for f in item_actions.ITEM_ACTIONS.keys()]

class ItemAction(models.Model):
    """Actions that the character can do with the item
    
    display_text Examples
    ---------------------
    If allow_char_target only then display as "Eat".
    If also allow_fight_target then display as "
    
    Target: Inventory Item would display as "use with _inventory item_"
    or "use with sword in inventory"
    
    TODO: Is there any reason for an item to target character or fight monster
    with same display text?
    If there isn't then should we specify multiple display_texts or
    have multiple item actions?
    
    IE. "Use (_Self_, _Fight_)" vs
    "_Use with Self_
     _Throw at enemy_"
     
    Note: It might in fact use the same function - or it might not.
    """
    CHAR = 'c'
    FIGHT = 'f'
    INV_ITEM = 'i'
    TARGET_CHOICES = (
        (CHAR, 'Character'),
        (FIGHT, 'Fight'),
        (INV_ITEM, 'Inventory Item')
    )
    
    name = models.CharField(max_length=100, unique=True)
    display_text = models.CharField(max_length=100)
    func = models.CharField(max_length=100)#, choices=get_item_action_choices())    
    
    target = models.CharField(max_length=1, choices=TARGET_CHOICES)
    
    allow_in_combat = models.BooleanField(default=False)
    allow_out_combat = models.BooleanField(default=False)


class Shop(models.Model):
    """Shops hold a collection of items available for purchase"""
    name = models.CharField(max_length=100, unique=True)
    inventory = models.ForeignKey('Inventory')
    
    def natural_key(self):
        return (self.name,)
    
    def __unicode__(self):
        return self.name



class Inventory(models.Model):
    """An inventory holding objects.
    You can hold unlimited different objects or upto a specified limit"""
    
    is_unlimited = models.BooleanField()
    size = models.PositiveIntegerField(default=0) #used only if not unlimited
    
    items = models.ManyToManyField(Item, through='InventoryItemInfo')
    
    class Meta:
        verbose_name = "inventory"
        verbose_name_plural = "inventories"
    
    def get_condensed_view(self):
        """Return a condensed view of the inventory
        
        condensed view = [(item1, total_num1), (item2, total_num2), ...]"""
        cv = {} #item: Total number of item
        for iii in self.inventoryiteminfo_set.all():
            if not iii.item in cv:
                cv[iii.item] = 0
            cv[iii.item] += iii.stack_size
        return cv.items()
    
    def get_iiis(self):
        """Return IIIs container for this inventory
        
        Can use this to get all or further filtering"""
        return self.inventoryiteminfo_set
    
    def get_size(self):
        """Return the size of the inventory (+infinite for unlimited)"""
        if self.is_unlimited:
            return float("inf")
        return self.size
    
    def has_free_slot(self):
        """Return if there is a slot free for a new item"""
        if self.is_unlimited:
            return True
        
        if self.items.count() < self.size:
            return True
        else:
            return False
    
    def num_free_slots(self):
        """Return number of free slots"""
        if self.is_unlimited:
            return float("inf")
        
        return self.size - len(self.inventoryiteminfo_set.all())
    
    def num_item(self, item):
        """Return how many of an item are in this inventory"""
        return sum([iii.stack_size for iii in self.get_iiis_of_item(item)])
    
    def get_iiis_of_item(self, item):
        return self.inventoryiteminfo_set.filter(item=item)
    
    def is_space_for_item(self, item, amount):
        """Can this inventory accommodate x items?"""
        if self.is_unlimited:
            return True
        elif item.is_unlimited_stack:
            #Check if there is an existing stack or a new one can be made
            if self.has_free_slot() or len(self.get_iiis_of_item(item)) > 0:
                return True
            return False
        else: #Check space in existing stacks and new stacks
            space_in_existing_stacks = 0
            for item_iii in self.get_iiis_of_item(item):
                space_in_existing_stacks += item_iii.free_stack_space()
            
            space_in_new_stacks = self.num_free_slots()*item.max_stack_size

            total_stack_space = space_in_existing_stacks + space_in_new_stacks
            
            return total_stack_space >= amount
    
    def change_items(self, doit, add_items=None, remove_items=None):
        """Can you add these items if you remove these other items?
        
        doit = If doit is False it will return whether it was possible and not
        actually do it.
        add_items = [ (item, quantity), ...]
        remove_items = [ (item, quantity), ...]
        
        If doit
            raise InventoryLacksSpace for error or return None for success
        otherwise return whether it is possible
        """
        if add_items is None:
            add_items = []
        if remove_items is None:
            remove_items = []
        
        class Te(Exception):
            def __init__(self, is_success):
                self.is_success = is_success
        
        try:
            with transaction.commit_on_success():
                for item, amount in remove_items:
                    self.remove_item(item, amount)
                
                try:
                    for item, amount in add_items:
                        self.add_item(item, amount)
                except InventoryLacksSpace:
                    if doit:
                        raise
                    else:
                        raise Te(False)
                else:
                    if not doit:
                        raise Te(True)
        except Te as T:
            return T.is_success


    def add_item(self, item, amount):
        """Add an item to this inventory"""
        #To add an item the following steps are taken:
        #1-Ensure this inventory has the space (check existing stacks)
        #2-Add item to existing stacks
        #3-Add item to new stacks
        if not self.is_space_for_item(item, amount):
            raise InventoryLacksSpace(self)
        
        if item.is_unlimited_stack:
            #2. Try to add to an existing slot
            try:
                item_iii = self.get_iiis_of_item(item)[0]
                item_iii.stack_size += amount
                item_iii.save()
            except IndexError:
                #3. Add it to a new slot
                InventoryItemInfo.objects.create(inventory=self,
                    item=item, stack_size=amount)
        else:
            #2. Add item to existing stacks
            for iii in self.get_iiis_of_item(item):
                can_add = min(iii.free_stack_space(), amount)
                iii.stack_size += can_add
                iii.save()
                amount -= can_add
                
                if amount == 0:
                    break
            
            #3. Add item to new stacks
            while amount > 0:
                can_add = min(item.max_stack_size, amount)
                InventoryItemInfo.objects.create(inventory=self, item=item,
                    stack_size=can_add)
                amount -= can_add
    
    def remove_item(self, item, amount=1):
        """Remove x items from this inventory and save.
        
        You may remove more items than there are in the inventory."""
        assert amount >= 1
        
        #Remove from the lowest stack size first
        for iii in self.get_iiis_of_item(item).order_by('stack_size'):
            remove_amount = min(iii.stack_size, amount)
            if remove_amount == iii.stack_size:
                iii.delete()
            else:
                iii.stack_size -= remove_amount
                iii.save()
            amount -= remove_amount
            
            if amount == 0:
                break
    
    
    
    def pickup_from(self, other_inventory, item, amount):
        """Transfer a amount number of items from another inventory to this one.
        
        (Note: This definitely does the action and saves the objects!)"""
        #To transfer an item
        #1-Ensure other inventory has the item.
        #2-Ensure this inventory has the space (check existing stacks)
        #3-Decrease item count from other inventory (remove item if necessary)
        #4-Add item to player's inventory (+1 to existing stack preferred)
        
        #NB: These checks are done now to prevent any actions from occuring
        #If there is a problem
        
        #Ensure other inventory has the item
        num_items_other_inventory = other_inventory.num_item(item)
        if num_items_other_inventory == 0:
            raise InventoryDoesNotHaveItem(other_inventory, item)
        elif num_items_other_inventory < amount:
            raise InventoryDoesNotHaveEnoughItems(other_inventory, item, amount)
        
        #Ensure this inventory has the space
        if not self.is_space_for_item(item, amount):
            raise InventoryLacksSpace(self, item, amount)
        
        #Remove item from the other inventory
        other_inventory.remove_item(item, amount)
        #Add item to this inventory
        self.add_item(item, amount)
    
    
    def __unicode__(self):
        def trychar():
            try:
                ci = Character.objects.get(inventory=self.pk)
                return ci.user_account.username+"'s Character Inventory"
            except Character.DoesNotExist:
                pass
        
        def tryshop():
            try:
                si = Shop.objects.get(inventory=self.pk)
                return si.name+"'s Shop Inventory"
            except Shop.DoesNotExist:
                pass
        
        for tryobj in [trychar, tryshop]:
            replacement = tryobj()
            if replacement:
                return replacement
       
        return "Noone's Inventory (pk:{0})".format(self.pk)


class InventoryItemInfo(models.Model):
    inventory = models.ForeignKey(Inventory)
    item = models.ForeignKey(Item)
    
    #The number of items in the stack
    stack_size = models.PositiveIntegerField()
    
    def free_stack_space(self):
        """Return the amount of space still free"""
        if self.item.is_unlimited_stack:
            return float("inf")
        
        return self.item.max_stack_size - self.stack_size
    
    def __unicode__(self):
        return unicode(self.inventory)+"/"+unicode(self.item)


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.ManyToManyField(Item, through='RecipeIngredientInfo',
                                         related_name="recipe_ingredients_set")
    products = models.ManyToManyField(Item, through='RecipeProductInfo',
                                      related_name='recipe_products_set')
    
    def ingredients_list(self):
        """Return the list [(ingredient, number), ...]"""
        lst = []
        for ingredient in self.ingredients.all():
            info = self.recipeingredientinfo_set.get(ingredient=ingredient)
            lst.append((ingredient, info.quantity))
        return lst
    
    def products_list(self):
        """Return the list [(product, number), ...]"""
        lst = []
        for product in self.products.all():
            info = self.recipeproductinfo_set.get(product=product)
            lst.append((product, info.quantity))
        return lst
    
    def __unicode__(self):
        return self.name


class RecipeIngredientInfo(models.Model):
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Item)
    quantity = models.IntegerField(default=1)


class RecipeProductInfo(models.Model):
    recipe = models.ForeignKey(Recipe)
    product = models.ForeignKey(Item)
    quantity = models.IntegerField(default=1)


class Message(models.Model):
    """A message to the player informing him of events across sessions/pages"""
    character = models.ForeignKey(Character)
    body = models.TextField()
