from django.db import models

class ItemManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class ItemPropertyManager(models.Manager):
    def get_by_natural_key(self, item, name):
        from game.models import Item
        return self.get(item=Item.objects.get_by_natural_key(*item), name=name)

class ItemActionManager(models.Manager):
    def get_by_natural_key(self, func):
        return self.get(func=func)

class ItemItemActionManager(models.Manager):
    def get_by_natural_key(self, item, item_action):
        from game.models import Item, ItemAction
        item_action_obj = ItemAction.objects.get_by_natural_key(*item_action)
        
        return self.get(item=Item.objects.get_by_natural_key(*item),
                        item_action=item_action_obj)


class MonsterManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ShopManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ShopStockInfoManager(models.Manager):
    def get_by_natural_key(self, shop, item):
        from game.models import Shop, Item
        shop_obj = Shop.objects.get_by_natural_key(*shop)
        item_obj = Item.objects.get_by_natural_key(*item)
        return self.get(shop=shop_obj, item=item_obj)


class RecipeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class RecipeIngredientInfoManager(models.Manager):
    def get_by_natural_key(self, recipe, ingredient):
        from game.models import Recipe, Item
        self.get(recipe=Recipe.objects.get_by_natural_key(*recipe),
                 ingredient=Item.objects.get_by_natural_key(*ingredient))

class RecipeProductInfoManager(models.Manager):
    def get_by_natural_key(self, recipe, product):
        from game.models import Recipe, Item
        self.get(recipe=Recipe.objects.get_by_natural_key(*recipe),
                 product=Item.objects.get_by_natural_key(*product))
