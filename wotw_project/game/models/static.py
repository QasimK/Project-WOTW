from django.db import models

import game.item_actions as item_actions


#---Models
class Monster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    hp = models.IntegerField()
    hp_dev = models.IntegerField(default=0)
    
    weapon = models.ForeignKey('Item', related_name="monster_weapons")
    armour = models.ForeignKey('Item', related_name="monster_armours")
    
    gold = models.IntegerField(default=0)
    gold_dev = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name


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
    
    def __str__(self):
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
    
    def __str__(self):
        return self.name


def get_item_action_choices():
    for f in item_actions.ITEM_ACTIONS.keys():
        yield (f,f)

class ItemAction(models.Model):
    """Actions that the character can do with the item"""
    TAR_CHAR = 'c'
    TAR_FIGHT = 'f'
    TAR_INV_ITEM = 'i'
    TARGET_CHOICES = (
        (TAR_CHAR, 'Character'),
        (TAR_FIGHT, 'Fight'),
        (TAR_INV_ITEM, 'Inventory Item')
    )
    
    func = models.CharField(max_length=100, unique=True,
                            choices=get_item_action_choices())
    
    target = models.CharField(max_length=1, choices=TARGET_CHOICES)
    
    allow_in_combat = models.BooleanField(default=False)
    allow_out_combat = models.BooleanField(default=False)
    
    def __str__(self):
        return self.func


class ItemItemActionInfo(models.Model):
    item = models.ForeignKey(Item)
    item_action = models.ForeignKey(ItemAction)
    display_text = models.CharField(max_length=100)


class Shop(models.Model):
    """Shops hold a collection of items available for purchase"""
    name = models.CharField(max_length=100, unique=True)
    inventory = models.ForeignKey('Inventory')
    
    def natural_key(self):
        return (self.name,)
    
    def __str__(self):
        return self.name



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
    
    def __str__(self):
        return self.name


class RecipeIngredientInfo(models.Model):
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Item)
    quantity = models.IntegerField(default=1)


class RecipeProductInfo(models.Model):
    recipe = models.ForeignKey(Recipe)
    product = models.ForeignKey(Item)
    quantity = models.IntegerField(default=1)


class Location(models.Model):
    name = models.CharField(max_length=100)
    can_goto_views = models.ManyToManyField('self', symmetrical=False,
                                            blank=True, null=True)
    
    def __str__(self):
        return self.name
