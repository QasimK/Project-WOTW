'''Save static game content into a fixture'''

from itertools import chain
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings 
from django.core import serializers

from game.models.static import *  # @UnusedWildImport

STANDARD_DB_FIXTURE = os.path.join(settings.BASE_DIR, 'content_fixture.json')

class Command(BaseCommand):
    args = '<full file path+name>'
    help = 'Save the static game content as a fixture'
    
    def handle(self, *args, **options):
        if len(args) > 1:
            raise CommandError("No more than one argument should be specified")
        
        # Must set inventory foreign key to null because inventory is dynamic
        def shops():
            shops = Shop.objects.all()
            for shop in shops:
                shop.inventory = None
            return shops
        
        # Must handle manual sorting of this for dependencies!
        save_models = chain(
            Item.objects.all(),
            ItemProperty.objects.all(),
            ItemAction.objects.all(),
            ItemItemActionInfo.objects.all(),
            Monster.objects.all(),
            shops(),
            ShopStockInfo.objects.all(),
            Recipe.objects.all(),
            RecipeIngredientInfo.objects.all(),
            RecipeProductInfo.objects.all()
        )
        
        fixture = serializers.serialize('json', save_models, indent=2,
          use_natural_foreign_keys=True, use_natural_primary_keys=True)
        
        try:
            with open(args[0], 'w') as f:
                f.write(fixture)
        except:
            with open(STANDARD_DB_FIXTURE, 'w') as f:
                f.write(fixture)
