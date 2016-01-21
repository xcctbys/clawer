from django.core.management.base import BaseCommand
from clawer_parse.parse import Parse


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        worker_henan = Parse('profiles/henan.json')
        worker_henan.parse_companies()

        # worker_hebei = Parse('profiles/hebei.json')
        # worker_hebei.parse_companies()
