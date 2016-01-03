# encoding=utf-8
""" example is http://roll.tech.sina.com.cn/s/channel.php?ch=05#col=30&spec=&type=&ch=05&k=&offset_page=0&offset_num=0&num=40&asc=&page=1
"""

import re
import logging
import json
import unittest
import requests
import traceback
import os
import datetime
import cPickle as pickle
try:
    import pwd
except:
    pass


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class History(object):

    def __init__(self):
        self.news_time_start = 20151021  # 设置开始日期
        self.count_date = 0  # 回溯日期间隔
        self.news_page = 1  # 新闻页码索引
        self.news_count = 1  # 当日新闻总数
        self.path = "tmp/sina_news"
        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))

    def load(self):
        if os.path.exists(self.path) is False:
            return

        with open(self.path, "r") as f:
            old = pickle.load(f)
            self.count_date = old.count_date
            self.news_page = old.news_page
            self.news_count = old.news_count

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)


class Generator(object):
    HOST = "http://roll.news.sina.com.cn/interface/rollnews_ch_out_interface.php?col=30&spec=&type=&date="

    def __init__(self):
        self.uris = set()
        self.history = History()
        self.history.load()

    def obtain_urls(self):
        date = (datetime.datetime.now() - datetime.timedelta(days=self.history.count_date)).strftime("%Y-%m-%d")  # 获取此次运行时需要抓取新闻的日期
        if int(date.replace("-", "")) < self.history.news_time_start:  # 判断回溯日期是否在设置的开始日期之前
            return

        url = self.HOST + str(date) + '&ch=05&k=&offset_page=0&offset_num=0&num=40&asc=&page=' + str(self.history.news_page)  # 构造url
        try:
            jscontent = requests.get(url).content.decode("gbk")  # 正则处理网页json后使用json.loads解析
            jscontent = jscontent.replace('var jsonData =', '')
            jscontent = jscontent.replace(';', '')
            jscontent = re.sub(r"(,?)(\w+?)\s+?:", r"\1'\2' :", jscontent)
            jscontent = jscontent.replace("'", "\"")
            js_dict = json.loads(jscontent)
            self.history.news_count = js_dict.get("count")  # 获取当日新闻数量
            js_list = js_dict.get("list")
            for each in js_list:
                self.uris.add(each.get("url"))
            self.history.news_page += 1  # 抓取完毕后页码索引加一并存入pickle
            self.history.save()
        except:
            self.history.news_page += 1
            self.history.save()
        if self.history.news_page > (self.history.news_count-1)/40+1:  # 判断页码索引是否大于当天最大页数
            self.history.count_date += 1
            self.history.news_page = 1
            self.history.news_count = 1
            self.history.save()


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()

        for uri in self.generator.uris:
            logging.debug("urls is %s", uri)

        logging.debug("urls count is %d", len(self.generator.uris))
        logging.debug("Date back is %d", self.generator.history.count_date)
        logging.debug("Current page is %d", self.generator.history.news_page)
        logging.debug("Current news count is %d", self.generator.history.news_count)

        self.assertGreater(len(self.generator.uris), 0)


if __name__ == "__main__":

    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_urls()

    for uri in generator.uris:
        print json.dumps({"uri": uri})
