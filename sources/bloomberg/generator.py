# encoding=utf-8
""" example is http://www.bloomberg.com/search?query=mac&startTime=-3m&page=1
"""

import urllib
import json
import logging
import unittest
import os
import requests
import cPickle as pickle
from bs4 import BeautifulSoup

try:
    import pwd
except:
    pass
import traceback


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


keywords = [
        'additive manufacturing',
        'rapid prototyping',
        '3D printing',
        '3D printer',
        'filament',
        'makerbot',
        'Wearable device',
        'Wearable smart device',
        'Smart Bracelet',
        'Smart Watch',
        'big data',
        'NoSQL database',
        'in-memory analytics',
        'Data Warehouse',
        'data mining',
        'machine learning',
        'Genetic testing',
        'DNA testing',
        'DNA sequencing',
        'Gene test',
        'genetic diagnosis',
        'Blood DNA test',
        'Body fluid DNA test',
        'Robot',
        'Industrial Robot AI',
        'Artificial Intelligence',
        'factory automation',
        'UAV',
        'Unmanned aerial vehicle',
        'remotely piloted aircraft',
        'RPA',
        'Drone revolution',
        'Drone Delivery',
        'Unmanned helicopter',
        'Unmanned fixed wing aircraft',
        'Unmanned airship',
        'Unmanned wing aircraft',
        'Internet of things',
        'IoT',
        'RFID',
        'M2M',
        'Internet of Everything',
        'New Energy',
        'alternative energy',
        'renewable energy',
        'clean energy',
        'Renewable energy',
        'Solar energy',
        'Wind energy',
        'Biomass energy',
        'Hydrogenic energy',
        'Geothermal energy',
        'Ocean energy',
        'Chemical energy',
        'Nuclear energy',
        'Mobile payment',
        'mobile money',
        'mobile money transfer',
        'mobile wallet',
        'NFC payment',
        'QR code payments',
        'cloud computing',
        'cloud safety',
        'cloud storage',
        'IaaS',
        'PaaS',
        'SaaS',
        'smart community',
        'Smart city',
        'Digital city',
        'Wireless city',
        'Mhealth',
        'Mobile health',
        'Mobile Healthcare',
        'Remote patient monitoring',
        'RPM',
        'telehealth',
        'eHealth',
        'Intelligent hospital system',
        'Regional health system',
        'Home health system',
        'Smart TV',
        'connected TV',
        'hybrid TV',
        'set-top box',
        'internet TV',
        'Online interactive media',
        'On-demanding streaming media',
        'Smart grid',
        'Smart Power Grids',
        'intelligent grid',
        'intelligent power grids',
        'Smart home',
        'home automation',
        'building automation',
        'intelligent home',
        'E-home',
        'digital home',
        'home networking',
        'Intelligent Vehicles',
        'Intelligent driving',
        'driverless car',
        'self-driving car',
        'autonomous vehicle',
        'electric vehicles',
        'Smart Phone',
        'smartphone',
        'tablet',
        'Tablet PC',
        'iPhone',
        'iPad',
        'Galaxy',
        'Surface Tablet',
        'Industrie 4.0',
        'smart factory',
        'Smart Manufacturing'
]


class History(object):

    def __init__(self):
        self.current_keyword = 0  # 关键词索引
        self.page_count = 1  # 页码索引
        self.path = "/tmp/bloombergThreeMonth"
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
            self.current_keyword = old.current_keyword
            self.page_count = old.page_count

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)



class Generator(object):
    HOST = 'http://www.bloomberg.com/search?'

    def __init__(self):
        self.uris = set()
        self.history = History()

        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))

        self.history.load()

    def obtain_urls(self):
        if self.history.current_keyword < 116:  # 判断关键词索引是否在范围内
            keyword = keywords[self.history.current_keyword]  # 根据索引提取关键词
            self.obtain_page(keyword)

    def obtain_page(self, keyword):  # 构造搜索结果页url并调用obtain_target_url函数（参数startTime为搜索的时间范围，-3m为三个月内，-1d为一天内）
        para = {"query": keyword.encode("utf8"), "startTime": "-3m", "page": self.history.page_count}
        url = self.HOST + urllib.urlencode(para)
        self.obtain_target_url(url)

    def obtain_target_url(self, current_url):
        r = requests.get(current_url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        soup = BeautifulSoup(r.text, "html5lib")
        count = int(soup.find("span", {"class": "search-category-facet__count active"}).get_text())  # 提取搜索结果页码中的文章总量
        if self.history.page_count <= (count - 1) / 10 + 1:  # 页码索引是否小于等于最大页码（每页十篇文章，最大页码通过文章总量计算得出）
            article = soup.find_all("div", {"class": "search-result"})  # 获取所有文章url所在标签的标签内容
            for each in article:  # 遍历每篇文章所在标签并提取文章url
                article = each.find_all("h1", {"class": "search-result-story__headline"})[0]
                article_url = article.find("a")["href"]
                if article_url != '':
                    uri = "http://www.bloomberg.com/" + article_url  # 构造目标文章url
                    self.uris.add(uri)
                else:
                    continue
            self.history.page_count += 1  # 提取当前页面后将页码索引加一
        else:
            self.history.current_keyword += 1  # 关键词索引加一
            self.history.page_count = 1  # 将页码索引重置为一
        self.history.save()


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()

        logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)


if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_urls()

    for uri in generator.uris:
        print json.dumps({"uri": uri})
