# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from clawer_parse.parse import Parse
from profiles.json_paths import json_paths
from multiprocessing import Pool
import os
import time


class Command(BaseCommand):

#    def handle(self, *args, **options):
#        for json_path in json_paths:
#            Parse(json_path).parse_companies()

    def handle(self, *args, **options):
        begin = time.time()
        p = Pool()

        for json_path in json_paths:
            p.apply_async(parse, args=(json_path,))

        p.close()
        p.join()

        end = time.time()
        secs = int(round(end - begin))
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)

        print "✅  Done！耗时 %d时%02d分%02d秒 ✅ " % (h, m, s)


def parse(json_path):
    worker = Parse(json_path)
    worker.parse_companies()
