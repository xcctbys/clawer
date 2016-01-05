#!/usr/bin/env python
#!encoding=utf-8
import os
import sys
import raven
import gzip
import random
import time
from datetime import datetime, timedelta

import logging
import Queue
import threading

ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings

from CaptchaRecognition import CaptchaRecognition
from crawler import CrawlerUtils
from beijing_crawler import BeijingCrawler
from jiangsu_crawler import JiangsuCrawler
from zongju_crawler import ZongjuCrawler
from shanghai_crawler import ShanghaiCrawler
from guangdong_crawler import GuangdongClawer


failed_ent = {}
province_crawler = {
    'beijing': BeijingCrawler,
    'jiangsu': JiangsuCrawler,
    'zongju': ZongjuCrawler,
    'shanghai': ShanghaiCrawler
    'guangdong' : GuangdongClawer
}

max_crawl_time = 0
start_crawl_time = None

def set_codecracker():
    for province in province_crawler.keys():
        province_crawler.get(province).code_cracker = CaptchaRecognition(province)


def config_logging():
    settings.logger = logging.getLogger('enterprise-crawler')
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


def crawl_work(n, province, json_restore_path, ent_queue):
    crawler = province_crawler[province](json_restore_path)
    while True:
        cur_time = datetime.now()
        if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
            settings.logger.info('crawl time over, exit!')
            while not ent_queue.empty():
                ent = ent_queue.get(timeout=3)
                ent_queue.task_done()
            break

        try:
            ent = ent_queue.get(timeout=3)
        except Exception as e:
            if ent_queue.empty():
                settings.logger.info('ent queue is empty, crawler %d stop' % n)
                return

        time.sleep(random.uniform(0.2, 1))
        settings.logger.info('crawler %d start to crawler enterprise(ent_id = %s)' % (n, ent))
        try:
            crawler.run(ent)
        except Exception as e:
            settings.logger.error('crawler %d failed to crawl enterprise(id = %s), with exception %s' %(n, ent, e))
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


def run(province, enterprise_list, json_restore_path):
    ent_queue = Queue.Queue()
    for x in enterprise_list:
        ent_queue.put(x)

    for i in range(settings.crawler_num):
        worker = threading.Thread(target=crawl_work,args=(i, province, json_restore_path, ent_queue))
        worker.start()
        time.sleep(random.uniform(1, 2))

    ent_queue.join()
    settings.logger.info('All crawlers work over')


def crawl_province(province, cur_date):
    #创建存储路径
    json_restore_dir = '%s/%s/%s/%s' % (settings.json_restore_path, p, cur_date[0], cur_date[1])
    if not os.path.exists(json_restore_dir):
        CrawlerUtils.make_dir(json_restore_dir)

    #获取企业名单
    enterprise_list = CrawlerUtils.get_enterprise_list(settings.enterprise_list_path + p + '.txt')

    #json存储文件名
    json_restore_path = '%s/%s.json' % (json_restore_dir, cur_date[2])

    #将企业名单放入队列
    ent_queue = Queue.Queue()
    for x in enterprise_list:
        ent_queue.put(x)

    #开启多个线程，每个线程均执行 函数 crawl_work
    for i in range(settings.crawler_num):
        worker = threading.Thread(target=crawl_work,args=(i, province, json_restore_path, ent_queue))
        worker.start()
        time.sleep(random.uniform(1, 2))

    #等待结束
    ent_queue.join()
    settings.logger.info('All %s crawlers work over' % province)

#    #压缩保存
#    with open(json_restore_path, 'r') as f:
#        compressed_data = zlib.compress(f.read())
#        compressed_json_restore_path = json_restore_path + '.gz'
#        with open(compressed_json_restore_path, 'wb') as cf:
#            cf.write(compressed_data)


    #压缩保存
    if not os.path.exists(json_restore_path):
        settings.logger.warn('json restore path %s does not exist!'%json_restore_path)
        return

    with open(json_restore_path, 'r') as f:
        data = f.read()
        compressed_json_restore_path = json_restore_path + '.gz'
        with gzip.open(compressed_json_restore_path, 'wb') as cf:
            cf.write(data)

    #删除json文件，只保留  .gz 文件
    os.remove(json_restore_path)


if __name__ == '__main__':
    config_logging()

    if not os.path.exists(settings.json_restore_path):
        CrawlerUtils.make_dir(settings.json_restore_path)

    if settings.sentry_open:
        settings.sentry_client = raven.Client(
            dsn=settings.sentry_dns,
        )

    set_codecracker()
    cur_date = CrawlerUtils.get_cur_y_m_d()

    if len(sys.argv) < 3:
        settings.logger.warn('usage: run.py max_crawl_time(minutes) province... (max_crawl_time 是最大爬取时间，以分钟计;province 是所要爬取的省份列表 用空格分开, all表示爬取全部)')
        exit(1)

    try:
        max_crawl_time = int(sys.argv[1])
        settings.max_crawl_time = timedelta(minutes=max_crawl_time)
    except ValueError as e:
        settings.logger.error('invalid max_crawl_time, should be a integer')
        exit(1)

    settings.logger.info('即将开始爬取，最长爬取时间为 %s' % settings.max_crawl_time)
    settings.start_crawl_time = datetime.now()

    if sys.argv[2] == 'all':
        for p in province_crawler.keys():
            cur_time = datetime.now()
            if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
                settings.logger.info('crawl time over, exit!')
                break
            crawl_province(p, cur_date)
    else:
        provinces = sys.argv[2:]
        for p in provinces:
            cur_time = datetime.now()
            if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
                settings.logger.info('crawl time over, exit!')
                break

            if not p in province_crawler.keys():
                settings.logger.warn('province %s is not supported currently' % p)
            else:
                crawl_province(p, cur_date)

