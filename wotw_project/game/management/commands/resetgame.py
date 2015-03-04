'''Reset/create the database
Load static game content from a fixture
Setup admin account
'''

from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Reset/create the database, load content and create admin account'
    
    def handle(self, *args, **options):
        try:
            call_command('flush')
        except RuntimeError:
            call_command('migrate')
        
        call_command('loaddata', 'initial_data')
        
        # Does not work inside eclipse - requires an external console
        call_command('createsuperuser')
