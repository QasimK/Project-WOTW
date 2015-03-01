'''
Created on 1 Sep 2010

@author: Qasim
'''

from django.contrib import admin

from game import models

def wepinfo(obj):
    s = "%s (%s)" % (str(obj.weapon), str(obj.weapon.prop_damage))
    if obj.weapon.is_soulbound:
        s += "*"
    return s
wepinfo.short_description = "Weapon (damage)"

def arminfo(obj):
    s = "%s (%s)" % (str(obj.armour), str(obj.armour.prop_damage_absorbed))
    if obj.armour.is_soulbound:
        s += "*"
    return s
arminfo.short_description = "Armour (damage absorbed)"



class MonsterAdmin(admin.ModelAdmin):
    list_display = ('name', 'hp', wepinfo, arminfo, 'gold')


def item_properties(item):
    props = item.itemproperty_set.all()
    s = ""
    for prop in props:
        s += "[{}: {}] ".format(prop.get_name_display(), str(prop.value))
    return s

def item_actions(item):
    iiais = item.itemitemactioninfo_set.all()
    s = ""
    for iiai in iiais:
        s += "[{}] ".format(iiai.display_text)
    return s

class ItemPropertyInfoInline(admin.TabularInline):
    model = models.ItemProperty
    extra = 1
    
class ItemItemActionInfoInline(admin.TabularInline):
    model = models.ItemItemActionInfo
    extra = 1

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_unlimited_stack', 'max_stack_size',
                   'is_soulbound', item_properties, item_actions)
    search_fields = ('name',)
    list_filter = ('itemproperty__name', 'is_unlimited_stack')
    fields = ('name', ('is_unlimited_stack', 'max_stack_size'),
              ('is_soulbound',))#, 'item_actions')
    inlines = [ItemPropertyInfoInline, ItemItemActionInfoInline]

#class ItemPropertyAdmin(admin.ModelAdmin):
#    list_display = ('name',)

class InventoryItemInfoInline(admin.TabularInline):
    model = models.InventoryItemInfo
    extra = 0

class ShopInline(admin.StackedInline):
    model = models.Shop
    fields = ('name',)
    readonly_fields = ('name',)
    has_add_permission = lambda s,r,o=None: False
    #has_change_permission = lambda s,r,o=None: False
    has_delete_permission = lambda s,r,o=None: False
    extra = 0

class CharInline(admin.StackedInline):
    model = models.Character
    fields = (('user_account', 'inventory_mode'),)
    readonly_fields = ('user_account', 'inventory_mode')
    has_add_permission = lambda s,r,o=None: False
    #has_change_permission = lambda s,r,o=None: False
    has_delete_permission = lambda s,r,o=None: False
    extra = 0

def inventory_owners(inventory):
    owners = []
    owners.extend(models.Character.objects.filter(inventory__pk=inventory.pk))
    owners.extend(models.Shop.objects.filter(inventory__pk=inventory.pk))
    return ''.join(['['+str(owner)+'] ' for owner in owners])

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', inventory_owners)
    inlines = [ShopInline, CharInline, InventoryItemInfoInline]


class ShopAdmin(admin.ModelAdmin):
    #list_display = ('name', 'inventory')
    #list_editable = ('inventory',)
    search_fields = ('name', )


class GameViewPropertyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'char', 'name', 'value')


def get_recipe_ingredients(recipe):
    return ', '.join(recipe.ingredients.values_list('name', flat=True))
get_recipe_ingredients.short_description = 'Ingredients'

def get_recipe_products(recipe):
    return ', '.join(recipe.products.values_list('name', flat=True))
get_recipe_products.short_description = 'Products'

class RecipeIngredientInfoInline(admin.TabularInline):
    model = models.RecipeIngredientInfo
    extra = 0

class RecipeProductInfoInline(admin.TabularInline):
    model = models.RecipeProductInfo
    extra = 0

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', get_recipe_products, get_recipe_ingredients)
    inlines = (RecipeIngredientInfoInline, RecipeProductInfoInline)


def get_goto_locations(location):
    return ', '.join(location.can_goto_views.values_list('name', flat=True))
get_goto_locations.short_description = 'Allowed locations to move to'

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', get_goto_locations)
    



admin.site.register(models.Character)
admin.site.register(models.Monster, MonsterAdmin)
admin.site.register(models.ActiveMonster)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.ItemProperty)#, ItemPropertyAdmin)
admin.site.register(models.ItemAction)
admin.site.register(models.Shop, ShopAdmin)
admin.site.register(models.Inventory, InventoryAdmin)
admin.site.register(models.InventoryItemInfo)
admin.site.register(models.GameViewProperty, GameViewPropertyAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Location, LocationAdmin)