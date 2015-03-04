'''Reset/create the database
Load static game content from a fixture
Set up admin account (with a corresponding character)
'''

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import models as models_auth

from game.models.dynamic import Character

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
        
        #Make a character
        Character.make_new_character(models_auth.User.objects.first())
