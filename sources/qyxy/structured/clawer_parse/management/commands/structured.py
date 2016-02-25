# -*- coding: utf-8 -*-

import gzip
import requests
import time
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from clawer_parse.parse import Parse
from clawer_parse.models import Basic
from multiprocessing import Pool
from datetime import date, timedelta
from cStringIO import StringIO
from configs import configs
from clawer_parse import multiprocessing_logging
from raven import Client

try:
    client = Client(settings.RAVEN_CONFIG["dsn"])
except:
    client = None


def wrapper_raven(fun):
    """
    wrapper for raven to trace manager commands
    """
    def wrap(cls, *args, **kwargs):
        try:
            return fun(cls, *args, **kwargs)
        except Exception, e:
            if client:
                client.captureException()
            else:
                raise e

    return wrap


class Command(BaseCommand):

    @wrapper_raven
    def handle(self, *args, **options):
        begin = time.time()
        p = Pool(processes=4)
        base_url = settings.JSONS_URL
        provinces = configs.PROVINCES
        suffix = ".json.gz"
        hours = ["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24"]
        prinvince = "test"

        config_logging()

        if not is_first_run():
            yesterday = date.today() - timedelta(0)
            yesterday_str = yesterday.strftime("%Y/%m/%d")

            for hour in hours:
                #url = base_url + "/" + prinvince + "/" + yesterday_str + suffix
                url = base_url + "/" + yesterday_str + "/" + hour + suffix 
                response = requests.get(url)

                if int(response.status_code) == 200:
                    gz = gzip.GzipFile(fileobj=StringIO(response.content))
                    companies = gz.readlines()
                    p.apply_async(parse, args=(companies, prinvince))

        else:
            for dec_day in reversed(range(0, 20)):
                yesterday = date.today() - timedelta(dec_day)
                yesterday_str = yesterday.strftime("%Y/%m/%d")

                for hour in hours:
                    #url = base_url+"/"+prinvince+"/"+yesterday_str+suffix
                    url = base_url + "/" + yesterday_str + "/" + hour + suffix 
                    response = requests.get(url)
                    print yesterday_str + "/" + hour + suffix

                    if int(response.status_code) == 200:
                        gz = gzip.GzipFile(fileobj=StringIO(response.content))
                        companies = gz.readlines()
                        p.apply_async(parse, args=(companies, prinvince))

        p.close()
        p.join()
        end = time.time()
        secs = round(end - begin)
        settings.logger.info("✅  Done! Cost " + str(secs) + "s ✅ ")


def is_first_run():
    is_first_run = Basic.objects.all()
    return not is_first_run


def parse(companies, prinvince):
    config_logging()
    worker = Parse(companies, prinvince)
    worker.parse_companies()


def config_logging():
    settings.logger = logging.getLogger('structured')
    settings.logger.setLevel(settings.LOG_LEVEL)
    fh = logging.FileHandler(settings.LOG_FILE)
    fh.setLevel(settings.LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(settings.LOG_FORMAT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    settings.logger.addHandler(fh)
    settings.logger.addHandler(ch)
    multiprocessing_logging.install_mp_handler(settings.logger)
