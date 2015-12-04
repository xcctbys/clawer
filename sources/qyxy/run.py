#!/usr/bin/env python
#!encoding=utf-8

import time
import Queue
import threading
from beijing_crawler import CrawlerBeijingEnt
from crawler import CheckCodeCracker
from crawler import CrawlerUtils
import settings

def crawl_work(n, ent_queue):
    crawler = CrawlerBeijingEnt(CheckCodeCracker())
    while True:
        try:
            ent = ent_queue.get(timeout=3)
        except Exception as e:
            if ent_queue.empty():
                print 'ent queue is empty, crawler %d stop' % n
                return

        time.sleep(1)
        print 'crawler %d start to crawler enterprise(ent_id = %s)' % (n, ent)
        try:
            crawler.crawl_work(ent)
        except Exception as e:
            print 'crawler %d failed to crawl enterprise(id = %s), with exception %s' %(n, ent, e)
            time.sleep(1)  # try again
            crawler.crawl_work(ent)
            raise e

        ent_queue.task_done()

def run():
    enterprise_list = CrawlerUtils.get_enterprise_list(settings.enterprise_list_path)
    ent_queue = Queue.Queue()
    for x in enterprise_list:
        ent_queue.put(x)

    for i in range(settings.crawler_num):
        worker = threading.Thread(target=crawl_work,args=(i, ent_queue))
        worker.start()
        time.sleep(2)

    ent_queue.join()
    print 'All crawlers work over'

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        if settings.sentry_open:
                settings.sentry_client.captureException()
    finally:
        pass

