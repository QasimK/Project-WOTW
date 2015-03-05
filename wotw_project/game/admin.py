from django.contrib import admin
from django.core.urlresolvers import reverse

from game.models import *


class ItemPropertyInfoInline(admin.TabularInline):
    model = ItemProperty
    extra = 1
    
class ItemItemActionInfoInline(admin.TabularInline):
    model = ItemItemActionInfo
    extra = 1

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

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_unlimited_stack', 'max_stack_size',
                   'is_soulbound', item_properties, item_actions)
    search_fields = ('name',)
    list_filter = ('itemproperty__name', 'is_unlimited_stack')
    fields = (
        ('name',),
        ('is_unlimited_stack', 'max_stack_size'),
        ('is_soulbound',)
    )
    inlines = [ItemPropertyInfoInline, ItemItemActionInfoInline]


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

@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'hp', wepinfo, arminfo, 'gold')


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

class InventoryItemInfoInline(admin.TabularInline):
    model = InventoryItemInfo
    extra = 0

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', inventory_owners)
    inlines = [ShopInline, CharInline, InventoryItemInfoInline]


def inventory_link(shop):
    link = reverse('admin:game_inventory_change', args=(shop.inventory.id,))
    return '<a href="{}">{}</a>'.format(link, shop.inventory)
inventory_link.allow_tags = True
inventory_link.short_description = 'Inventory'

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'item_table', inventory_link)    


@admin.register(GameViewProperty)
class GameViewPropertyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'char', 'name', 'value')


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

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', get_recipe_products, get_recipe_ingredients)
    inlines = (RecipeIngredientInfoInline, RecipeProductInfoInline)


def get_goto_locations(location):
    return ', '.join(location.can_goto_views.values_list('name', flat=True))
get_goto_locations.short_description = 'Allowed locations to move to'

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', get_goto_locations)
    



admin.site.register(Character)
admin.site.register(ActiveMonster)
#admin.site.register(ItemProperty)
admin.site.register(ItemAction)
admin.site.register(ItemTable)
admin.site.register(ItemTableItemInfo)
#admin.site.register(InventoryItemInfo)
