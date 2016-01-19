from django.core.management.base import BaseCommand
from clawer_parse.parse import Parse


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        worker = Parse('profiles/test1.json')
        worker.handle_companies()
