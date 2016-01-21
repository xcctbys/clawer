#!/usr/bin/env python
#!encoding=utf-8
import os
import sys
import raven
import gzip
import random
import time
import datetime
import stat

import logging
import Queue
import threading
import multiprocessing
import socket

ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings

from mail import SendMail

from CaptchaRecognition import CaptchaRecognition
from crawler import CrawlerUtils
from beijing_crawler import BeijingCrawler
from jiangsu_crawler import JiangsuCrawler
from zongju_crawler import ZongjuCrawler
from shanghai_crawler import ShanghaiCrawler
from guangdong_crawler import GuangdongClawer
from heilongjinag_crawler import HeilongjiangClawer
from anhui_crawler import AnhuiCrawler
from yunnan_crawler import YunnanCrawler
from tianjin_crawler import TianjinCrawler
from hunan_crawler import HunanCrawler
from fujian_crawler import FujianCrawler
from sichuan_crawler import SichuanCrawler
from shandong_crawler import ShandongCrawler
from hebei_crawler import HebeiCrawler
from shaanxi_crawler import ShaanxiCrawler
from henan_crawler import HenanCrawler
from neimenggu_crawler import NeimengguClawer
from chongqing_crawler import ChongqingClawer
#from xinjiang_crawler import XinjiangClawer
from zhejiang_crawler import ZhejiangCrawler

failed_ent = {}
province_crawler = {
    'beijing': BeijingCrawler,
    'jiangsu': JiangsuCrawler,
    'zongju': ZongjuCrawler,
    'shanghai': ShanghaiCrawler,
    'guangdong': GuangdongClawer,
    'heilongjiang': HeilongjiangClawer,
    'anhui': AnhuiCrawler,
    'yunnan':YunnanCrawler,
    'tianjin' : TianjinCrawler,
    'hunan' : HunanCrawler,
    'fujian' : FujianCrawler,
    'sichuan': SichuanCrawler,
    'shandong' : ShandongCrawler,
    'hebei' : HebeiCrawler,
    'neimenggu':NeimengguClawer,
    'shaanxi': ShaanxiCrawler,
    'henan' : HenanCrawler,
    #'xinjiang':XinjiangClawer,
    'chongqing':ChongqingClawer,
    'zhejiang' : ZhejiangCrawler,
}

max_crawl_time = 0


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

    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(pathname)s:%(lineno)d:: %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    settings.logger.addHandler(fh)
    settings.logger.addHandler(ch)


def crawl_work(n, province, json_restore_path, ent_queue):
    crawler = province_crawler[province](json_restore_path)

    while True:

        try:
            ent = ent_queue.get(timeout=3)
        except Exception as e:
            if ent_queue.empty():
                settings.logger.info('ent queue is empty, crawler %d stop' % n)
                break

        time.sleep(random.uniform(0.2, 1))
        settings.logger.info('crawler %d start to crawler enterprise(ent_id = %s)' % (n, ent))
        try:
            crawler.run(ent)
        except Exception as e:
            settings.logger.error('crawler %s failed to get enterprise(id = %s), with exception %s' % (province, ent, e))
            """
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
            """
        finally:
            ent_queue.task_done()


def crawl_province(province, cur_date):
    #创建存储路径
    json_restore_dir = '%s/%s/%s/%s' % (settings.json_restore_path, province, cur_date[0], cur_date[1])
    if not os.path.exists(json_restore_dir):
        CrawlerUtils.make_dir(json_restore_dir)

    #获取企业名单
    enterprise_list = CrawlerUtils.get_enterprise_list(settings.enterprise_list_path + province + '.txt')

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

    #压缩保存
    if not os.path.exists(json_restore_path):
        settings.logger.warn('json restore path %s does not exist!' % json_restore_path)
        os._exit(1)
        return

    with open(json_restore_path, 'r') as f:
        data = f.read()
        compressed_json_restore_path = json_restore_path + '.gz'
        with gzip.open(compressed_json_restore_path, 'wb') as cf:
            cf.write(data)

    #删除json文件，只保留  .gz 文件
    os.remove(json_restore_path)
    os._exit(0)


def force_exit():
    settings.logger.error("run timeout")
    os._exit(1)


class Checker(object):
    """ Is obtain data from province enterprise site today ?
    """
    def __init__(self):
        self.yesterday = datetime.datetime.now() - datetime.timedelta(1)
        self.parent = settings.json_restore_path
        self.success = [] # {'name':'', "size':0}
        self.failed = [] # string list
        self.send_mail = SendMail(settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD, ssl=True)

    def run(self):
        for province in sorted(province_crawler.keys()):
            path = self._json_path(province)
            if os.path.exists(path) is False:
                self.failed.append(province)
                continue

            st = os.stat(path)
            self.success.append({"name": province, "size": st[stat.ST_SIZE]})

        #output
        settings.logger.error("success %d, failed %d", len(self.success), len(self.failed))
        for item in self.success:
            settings.logger.error("\t%s: %d bytes", item['name'], item['size'])

        settings.logger.error("Failed province")
        for item in self.failed:
            settings.logger.error("\t%s", item)

        self._report()

    def _json_path(self, province):
        path = os.path.join(self.parent, province, self.yesterday.strftime("%Y/%m/%d.json.gz"))
        return path

    def _report(self):
        title = u"%s 企业信用爬取情况" % (self.yesterday.strftime("%Y-%m-%d"))
        content = u"Stat Info. Success %d, failed %d\r\n" % (len(self.success), len(self.failed))

        content += u"Success province:\n"
        for item in self.success:
            content += u"\t%s: %d bytes\n" % (item["name"], item['size'])

        content += u"Failed province:\n"
        for item in self.failed:
            content += u"\t%s\n" % (item)

        content += u"\r\n -- from %s" % socket.gethostname()

        to_admins = [x[1] for x in settings.ADMINS]

        self.send_mail.send(settings.EMAIL_HOST_USER, to_admins, title, content)







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

    if len(sys.argv) == 2 and sys.argv[1] == "check":
        checker = Checker()
        checker.run()
        exit(0)
    elif len(sys.argv) < 3:
        print 'usage: run.py [check] [max_crawl_time(minutes) province...] \n\tmax_crawl_time 最大爬取时间，以秒计;\n\tprovince 是所要爬取的省份列表 用空格分开, all表示爬取全部)'
        exit(1)

    try:
        max_crawl_time = int(sys.argv[1])
        settings.max_crawl_time = datetime.timedelta(minutes=max_crawl_time)
    except ValueError as e:
        settings.logger.error('invalid max_crawl_time, should be a integer')
        os._exit(1)

    timer = threading.Timer(max_crawl_time, force_exit)
    timer.start()

    settings.logger.info(u'即将开始爬取，最长爬取时间为 %s 秒' % settings.max_crawl_time)
    settings.start_crawl_time = datetime.datetime.now()

    if sys.argv[2] == 'all':
        for p in sorted(province_crawler.keys()):
            process = multiprocessing.Process(target=crawl_province, args=(p, cur_date))
            process.daemon = True
            process.start()
            process.join(max_crawl_time/2)
    else:
        provinces = sys.argv[2:]
        for p in provinces:
            if not p in province_crawler.keys():
                settings.logger.warn('province %s is not supported currently' % p)
            else:
                process = multiprocessing.Process(target=crawl_province, args=(p, cur_date))
                process.daemon = True
                process.start()
                process.join(max_crawl_time)
                settings.logger.info("child process exit code %d", process.exitcode)

    os._exit(0)

