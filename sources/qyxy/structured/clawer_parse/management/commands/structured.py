# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from clawer_parse.parse import Parse
from multiprocessing import Pool
from profiles import consts
from profiles import consts
from datetime import date, timedelta
from cStringIO import StringIO
import gzip
import requests
import time


class Command(BaseCommand):

    def handle(self, *args, **options):
        begin = time.time()
        p = Pool(processes=16)
        base_url = consts.JSONS_URL
        provinces = consts.PROVINCES
        yesterday = date.today() - timedelta(1)
        yesterday_str = yesterday.strftime("%Y/%m/%d")
        suffix = ".json.gz"

        for prinvince in provinces:
            url = base_url + "/" + prinvince + "/" + yesterday_str + suffix
            response = requests.get(url)

            if int(response.status_code) == 200:
                gz = gzip.GzipFile(fileobj=StringIO(response.content))
                companies = gz.readlines()
                p.apply_async(parse, args=(companies,))

        p.close()
        p.join()

        end = time.time()
        secs = int(round(end - begin))
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        print "✅  Done！耗时 %d时%02d分%02d秒 ✅ " % (h, m, s)


def parse(companies):
    worker = Parse(companies)
    worker.parse_companies()
