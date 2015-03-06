from django.contrib import admin
from django.core.urlresolvers import reverse

from game.models import *


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    class ItemPropertyInfoInline(admin.TabularInline):
        model = ItemProperty
        extra = 1
    
    class ItemItemActionInfoInline(admin.TabularInline):
        model = ItemItemActionInfo
        extra = 1
    
    list_display = ('name', 'is_unlimited_stack', 'max_stack_size',
                   'is_soulbound', 'get_item_properties', 'get_item_actions')
    
    search_fields = ('name',)
    list_filter = ('itemproperty__name', 'is_unlimited_stack')
    fields = (
        ('name',),
        ('is_unlimited_stack', 'max_stack_size'),
        ('is_soulbound',)
    )
    inlines = [ItemPropertyInfoInline, ItemItemActionInfoInline]
    
    def get_item_properties(self, item):
        props = item.itemproperty_set.all()
        return ' '.join(['[{}: {}]'.format(prop.get_name_display(), prop.value)
                         for prop in props])
    get_item_properties.short_description = 'Item properties'
    
    def get_item_actions(self, item):
        iiais = item.itemitemactioninfo_set.all()
        return ' '.join(['[{}]'.format(iiai.display_text) for iiai in iiais])
    get_item_actions.short_description = 'Item actions'


@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'hp', 'get_wepinfo', 'get_arminfo', 'gold')

    def get_wepinfo(self, obj):
        s = "%s (%s)" % (str(obj.weapon), str(obj.weapon.prop_damage))
        if obj.weapon.is_soulbound:
            s += "*"
        return s
    get_wepinfo.short_description = "Weapon (damage)"
    
    def get_arminfo(self, obj):
        s = "%s (%s)" % (str(obj.armour), str(obj.armour.prop_damage_absorbed))
        if obj.armour.is_soulbound:
            s += "*"
        return s
    get_wepinfo.short_description = "Armour (damage absorbed)"


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    class ItemInline(admin.TabularInline):
        model = Shop.stock.through
        extra = 0
    
    search_fields = ('name', 'shopstockinfo__item__name')
    list_display = ('name', 'get_stock', 'inventory_link')
    
    exclude = ('inventory',)
    readonly_fields = ('inventory_link',)
    inlines = [ItemInline]
    
    def get_stock(self, shop):
        return ', '.join([str(s) for s in shop.stock.all()])
    get_stock.short_description = 'Stock items'

    def inventory_link(self, shop):
        link = reverse('admin:game_inventory_change', args=(shop.inventory.id,))
        return '<a href="{}">{}</a>'.format(link, shop.inventory)
    inventory_link.allow_tags = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    class RecipeIngredientInfoInline(admin.TabularInline):
        model = RecipeIngredientInfo
        extra = 0
    
    class RecipeProductInfoInline(admin.TabularInline):
        model = RecipeProductInfo
        extra = 0
    
    list_display = ('name', 'get_recipe_products', 'get_recipe_ingredients')
    inlines = (RecipeIngredientInfoInline, RecipeProductInfoInline)
    
    def get_recipe_ingredients(self, recipe):
        return ', '.join(recipe.ingredients.values_list('name', flat=True))
    get_recipe_ingredients.short_description = 'Ingredients'
    
    def get_recipe_products(self, recipe):
        return ', '.join(recipe.products.values_list('name', flat=True))
    get_recipe_products.short_description = 'Products'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_goto_locations')

    def get_goto_locations(self, location):
        return ', '.join(location.can_goto_views.values_list('name', flat=True))
    get_goto_locations.short_description = 'Allowed locations to move to'


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
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
    
    class InventoryItemInfoInline(admin.TabularInline):
        model = InventoryItemInfo
        extra = 0
    
    list_display = ('__str__', 'get_inventory_owners')
    
    inlines = [ShopInline, CharInline, InventoryItemInfoInline]
    
    def get_inventory_owners(self, inventory):
        owners = []
        owners.extend(Character.objects.filter(inventory__pk=inventory.pk))
        owners.extend(Shop.objects.filter(inventory__pk=inventory.pk))
        return ''.join(['['+str(owner)+'] ' for owner in owners])


@admin.register(GameViewProperty)
class GameViewPropertyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'char', 'name', 'value')



admin.site.register(Character)
admin.site.register(ActiveMonster)
#admin.site.register(ItemProperty)
admin.site.register(ItemAction)
#admin.site.register(InventoryItemInfo)
