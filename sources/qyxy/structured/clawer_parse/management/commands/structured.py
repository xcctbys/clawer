# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from clawer_parse.parse import Parse
from profiles.json_paths import json_paths


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        for json_path in json_paths:
            print "\n正在解析%s..." % json_path
            Parse(json_path).parse_companies()
