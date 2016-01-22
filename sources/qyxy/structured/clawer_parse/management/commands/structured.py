# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from clawer_parse.parse import Parse
from profiles.json_paths import json_paths
from multiprocessing import Pool
import os


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        print 'Parent process %s.' % os.getpid()
        p = Pool()

        for json_path in json_paths:
            p.apply_async(parse, args=(json_path,))

        p.close()
        p.join()
        print "✅  All subprocesses done. ✅ "

def parse(json_path):
    print "\n正在解析 %s，进程ID：%s..." % (json_path, os.getpid())
    Parse(json_path).parse_companies()
    print "✅  %s 解析完成。 ✅ " % json_path
