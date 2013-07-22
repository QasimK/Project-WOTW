'''
Created on 1 Sep 2010

@author: Qasimk
'''

from django.contrib import admin

from wotw_project.game.models import (
    Character, GameViewProperty, Monster, ActiveMonster,
    Item, ItemProperty,
    Shop, Inventory, InventoryItemInfo,
    Recipe, RecipeIngredientInfo, RecipeProductInfo)

def wepinfo(obj):
    s = "%s (%s)" % (str(obj.weapon), str(obj.weapon.damage))
    if obj.weapon.soulbound:
        s += "*"
    return s
wepinfo.short_description = "Weapon"

def arminfo(obj):
    s = "%s (%s" % (str(obj.armour), str(obj.armour.absorption)) +r"%)"
    if obj.armour.soulbound:
        s += "*"
    return s
arminfo.short_description = "Armour"

class MonsterAdmin(admin.ModelAdmin):
    list_display = ('name', 'hp', 'weapon', 'armour', 'gold')


def item_properties(item):
    props = item.itemproperty_set.all()
    return ''.join(["["+str(prop.get_name_display())+"] " for prop in props])

class ItemPropertyInfoInline(admin.TabularInline):
    model = ItemProperty
    extra = 1

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_unlimited_stack', 'max_stack_size',
                    item_properties)
    search_fields = ('name',)
    list_filter = ('itemproperty__name', 'is_unlimited_stack')
    fields = ('name', ('is_unlimited_stack', 'max_stack_size'))
    inlines = [ItemPropertyInfoInline]

#class ItemPropertyAdmin(admin.ModelAdmin):
#    list_display = ('name',)

class InventoryItemInfoInline(admin.TabularInline):
    model = InventoryItemInfo
    extra = 0

class ShopInline(admin.StackedInline):
    model = Shop
    fields = ('name',)
    readonly_fields = ('name',)
    has_add_permission = lambda s,r,o=None: False
    #has_change_permission = lambda s,r,o=None: False
    has_delete_permission = lambda s,r,o=None: False
    extra = 0

class CharInline(admin.StackedInline):
    model = Character
    fields = (('user_account', 'inventory_mode'),)
    readonly_fields = ('user_account', 'inventory_mode')
    has_add_permission = lambda s,r,o=None: False
    #has_change_permission = lambda s,r,o=None: False
    has_delete_permission = lambda s,r,o=None: False
    extra = 0

def inventory_owners(inventory):
    owners = []
    owners.extend(Character.objects.filter(inventory__pk=inventory.pk))
    owners.extend(Shop.objects.filter(inventory__pk=inventory.pk))
    return ''.join(['['+str(owner)+'] ' for owner in owners])

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', inventory_owners)
    inlines = [ShopInline, CharInline, InventoryItemInfoInline]


class ShopAdmin(admin.ModelAdmin):
    #list_display = ('name', 'inventory')
    #list_editable = ('inventory',)
    search_fields = ('name', )


def gvp_name(obj):
    return str(obj)

class GameViewPropertyAdmin(admin.ModelAdmin):
    list_display = (gvp_name, 'char', 'name', 'value')


def get_recipe_ingredients(recipe):
    return ', '.join(recipe.ingredients.values_list('name', flat=True))
get_recipe_ingredients.short_description = 'Ingredients'

def get_recipe_products(recipe):
    return ', '.join(recipe.products.values_list('name', flat=True))
get_recipe_products.short_description = 'Products'

class RecipeIngredientInfoInline(admin.TabularInline):
    model = RecipeIngredientInfo
    extra = 0

class RecipeProductInfoInline(admin.TabularInline):
    model = RecipeProductInfo
    extra = 0

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', get_recipe_products, get_recipe_ingredients)
    inlines = (RecipeIngredientInfoInline, RecipeProductInfoInline)


admin.site.register(Character)
admin.site.register(Monster, MonsterAdmin)
admin.site.register(ActiveMonster)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemProperty)#, ItemPropertyAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryItemInfo)
admin.site.register(GameViewProperty, GameViewPropertyAdmin)
admin.site.register(Recipe, RecipeAdmin)
