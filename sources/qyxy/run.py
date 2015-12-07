#!/usr/bin/env python
#!encoding=utf-8
import os
import raven
import urllib2
import random
import time
import logging
import Queue
import threading
from beijing_crawler import CrawlerBeijingEnt
from crawler import CheckCodeCracker
from crawler import CrawlerUtils
import settings
failed_ent = {}

def config_logging():
    settings.logger = logging.getLogger('beijing-enterprise-crawler')
    settings.logger.setLevel(settings.log_level)
    fh = logging.FileHandler(settings.log_file)
    fh.setLevel(settings.log_level)
    ch = logging.StreamHandler()
    ch.setLevel(settings.log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    settings.logger.addHandler(fh)
    settings.logger.addHandler(ch)

def crawl_work(n, ent_queue):
    crawler = CrawlerBeijingEnt(CheckCodeCracker())
    while True:
        try:
            ent = ent_queue.get(timeout=3)
        except Exception as e:
            if ent_queue.empty():
                settings.logger.info('ent queue is empty, crawler %d stop' % n)
                return

        time.sleep(random.uniform(0.2, 1))
        settings.logger.info('crawler %d start to crawler enterprise(ent_id = %s)' % (n, ent))
        try:
            crawler.crawl_work(ent)
        except Exception as e:
            settings.logger.error('crawler %d failed to crawl enterprise(id = %s), with exception %s' %(n, ent, e))
            # if (isinstance(e, urllib2.HTTPError) and e.code == 500) or (isinstance(e, urllib2.URLError) and e.code == 54):
            #     settings.logger.info('failed to crawl enterprise(id = %s) with %s, push it into queue again to crawl it later' % (ent, e))
            #     ent_queue.put(ent)

            if failed_ent.get(ent, 0) > 3:
                settings.logger.error('Failed to crawl and parse enterprise %s' % ent)
                #report to sentry
                if settings.sentry_open:
                    settings.sentry_client.captureException()
                return  #end this thread

            else:
                failed_ent[ent] = failed_ent.get(ent, 0) + 1
                settings.logger.warn('failed to crawl enterprise(id = %s) %d times!' % (ent, failed_ent[ent]))
                ent_queue.put(ent)
        finally:
            ent_queue.task_done()


def run():
    enterprise_list = CrawlerUtils.get_enterprise_list(settings.enterprise_list_path)
    ent_queue = Queue.Queue()
    for x in enterprise_list:
        ent_queue.put(x)

    for i in range(settings.crawler_num):
        worker = threading.Thread(target=crawl_work,args=(i, ent_queue))
        worker.start()
        time.sleep(random.uniform(1, 2))

    ent_queue.join()
    settings.logger.info('All crawlers work over')

if __name__ == '__main__':
    config_logging()
    if not os.path.exists(settings.json_restore_path):
        CrawlerUtils.make_dir(settings.json_restore_path)

    settings.json_restore_path += ('/' + CrawlerUtils.get_cur_time() + '.json')


    if settings.sentry_open:
        settings.sentry_client =  raven.Client(
            dsn=settings.sentry_dns,
        )
    run()
