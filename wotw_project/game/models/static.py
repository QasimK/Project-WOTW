from django.db import models

from game import item_actions
from game.models.managers import *

#---Models
class Item(models.Model):
    """Items have a unique name.
    
    Shops ignore the max_stack_size.
    max_stack_size is used for player inventories."""
    objects = ItemManager()
    
    name = models.CharField(max_length=100, unique=True)
    
    # It can either stack forever, or max_stack_size is used
    is_unlimited_stack = models.BooleanField(default=False)
    max_stack_size = models.PositiveIntegerField(default=1)
    
    # Determines if looting and trading the item is possible
    is_soulbound = models.BooleanField(default=False)
    
    item_actions = models.ManyToManyField('ItemAction',
                                          through='ItemItemActionInfo')
    
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
        '''Return the value of the item - used by shops'''
        prop = self.itemproperty_set.get(name=ItemProperty.COST)
        return int(prop.value)
    
    @property
    def prop_health_healed(self):
        prop = self.itemproperty_set.get(name=ItemProperty.HEALTH_HEALED)
        return int(prop.value)
    
    def get_props(self):
        """Return all properties in format [(nice name, value), ...]"""
        props = self.itemproperty_set.all()
        return [(prop.get_name_display(), prop.value) for prop in props]
    
    def get_item_actions(self):
        """Return a list of [item_action object, display text]"""
        return [(i.item_action, i.display_text) for i in
                self.itemitemactioninfo_set.all()]
    
    def natural_key(self):
        return (self.name,)
    
    def __str__(self):
        return self.name


class ItemProperty(models.Model):
    """A property on an item - (item, item property name) is unique"""
    objects = ItemPropertyManager()
    
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
        unique_together = ("item", "name")
    
    def natural_key(self):
        return (self.item.natural_key(), self.name)
    natural_key.dependencies = ['game.item']
    
    def __str__(self):
        return self.name


class ItemAction(models.Model):
    """Actions that the character can do with the item
    
    The func (item action function) is a unique string"""
    objects = ItemActionManager()
    
    TAR_CHAR = 'c'
    TAR_FIGHT = 'f'
    TAR_INV_ITEM = 'i' #TODO: What does that mean?
    TARGET_CHOICES = (
        (TAR_CHAR, 'Character'),
        (TAR_FIGHT, 'Fight'),
        (TAR_INV_ITEM, 'Inventory Item')
    )
    
    func = models.CharField(max_length=100, unique=True,
                            choices=item_actions.get_item_action_choices())
    
    target = models.CharField(max_length=1, choices=TARGET_CHOICES)
    
    allow_in_combat = models.BooleanField(default=False)
    allow_out_combat = models.BooleanField(default=False)
    
    def natural_key(self):
        return (self.func, )
    
    def __str__(self):
        return self.func


class ItemItemActionInfo(models.Model):
    objects = ItemItemActionManager()
    
    item = models.ForeignKey(Item)
    item_action = models.ForeignKey(ItemAction)
    display_text = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('item', 'item_action')
    
    def natural_key(self):
        return (self.item.natural_key(), self.item_action.natural_key())
    natural_key.dependencies = ['game.Item', 'game.ItemAction']


class Monster(models.Model):
    '''Monsters have a unique name'''
    objects = MonsterManager()
    
    name = models.CharField(max_length=100, unique=True)
    
    hp = models.IntegerField()
    hp_dev = models.IntegerField(default=0)
    
    weapon = models.ForeignKey('Item', related_name="monster_weapons")
    armour = models.ForeignKey('Item', related_name="monster_armours")
    
    gold = models.IntegerField(default=0)
    gold_dev = models.IntegerField(default=0)
    
    def natural_key(self):
        return (self.name,)
    natural_key.dependencies = ['game.Item']
    
    def __str__(self):
        return self.name


class Shop(models.Model):
    """Shops hold a collection of items available for purchase"""
    objects = ShopManager()
    
    name = models.CharField(max_length=100, unique=True)
    inventory = models.ForeignKey('Inventory', null=True, blank=True)
    
    def natural_key(self):
        return (self.name,)
    
    def __str__(self):
        return self.name



class Recipe(models.Model):
    '''Recipes have unique names'''
    objects = RecipeManager()
    
    name = models.CharField(max_length=100, unique=True)
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
    
    def natural_key(self):
        return (self.name,)
    
    def __str__(self):
        return self.name


class RecipeIngredientInfo(models.Model):
    objects = RecipeIngredientInfoManager()
    
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Item)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ('recipe', 'ingredient')
    
    def natural_key(self):
        return (self.recipe.natural_key(), self.ingredient.natural_key())
    natural_key.dependencies = ['game.Recipe', 'game.Item']


class RecipeProductInfo(models.Model):
    objects = RecipeProductInfoManager()
    
    recipe = models.ForeignKey(Recipe)
    product = models.ForeignKey(Item)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ('recipe', 'product')
    
    def natural_key(self):
        return (self.recipe.natural_key(), self.product.natural_key())
    natural_key.dependencies = ['game.Recipe', 'game.Item']


# TODO: Not yet used
class Location(models.Model):
    name = models.CharField(max_length=100)
    can_goto_views = models.ManyToManyField('self', symmetrical=False,
                                            blank=True, null=True)
    
    def __str__(self):
        return self.name
