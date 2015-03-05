'''Reset/create the database
Load static game content from a fixture
Set up admin account (with a corresponding character)
'''

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import models as models_auth

from game.models.static import Shop, ItemTableItemInfo
from game.models.dynamic import Character, Inventory

class Command(BaseCommand):
    help = 'Reset/create the database, load content and create an admin account'
    
    def handle(self, *args, **options):
        try:
            call_command('flush')
        except RuntimeError:
            call_command('migrate')
        
        call_command('loaddata', 'initial_data')
        
        # Does not work inside eclipse - requires an external console
        call_command('createsuperuser')
        
        #Make a character for the admin account
        Character.make_new_character(models_auth.User.objects.first())
        
        #Give shops inventories and their initial stock.
        for shop in Shop.objects.all():
            inventory = Inventory.objects.create()
            
            itiis = ItemTableItemInfo.objects.filter(item_table=shop.item_table)
            for itemtableiteminfo in itiis:
                item = itemtableiteminfo.item
                quantity = itemtableiteminfo.quantity
                inventory.add_item(item, quantity)
            
            shop.inventory = inventory
            shop.save()
