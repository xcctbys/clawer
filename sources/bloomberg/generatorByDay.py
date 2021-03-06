# encoding=utf-8
""" example is http://www.bloomberg.com/search?query=additive+manufacturing
"""


import urllib
import json
import logging
import unittest
import os
import datetime
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
        self.current_keyword = 0
        self.current_count = 117
        self.current_time = datetime.datetime.now()
        self.path = "/tmp/bloomberg"
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
            if old.current_time.strftime("%Y-%m-%d") == self.current_time.strftime("%Y-%m-%d"):  # pickle内时间与当前时间一致则继续爬取
                self.current_keyword = old.current_keyword
                self.current_count = old.current_count
            else:  # pickle内时间与当前时间不一致则重置索引值
                self.current_keyword = 0
                self.current_count = 117

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)


class Generator(object):
    HOST = 'http://www.bloomberg.com/search?'
    STEP = 11
    dateSTEP = 2

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
        if self.history.current_count <= 0:
            return
        if self.history.current_count < self.STEP - 1:
            self.STEP = self.history.current_count
        for i in range(1, self.STEP):
            keyword = keywords[self.history.current_keyword]
            self.obtain_page(keyword)

        self.history.current_count -= self.STEP - 1
        self.history.save()

    def obtain_page(self, keyword):
        for i in range(1, self.dateSTEP):
            url = self.HOST + urllib.urlencode({"query": keyword.encode("utf8")}) + '&startTime=-1d'
            self.obtain_target_url(url)
        self.history.current_keyword += 1
        self.history.save()

    def obtain_target_url(self, current_url):
        r = requests.get(current_url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        soup = BeautifulSoup(r.text, "html5lib")
        article = soup.find_all("div", {"class": "search-result"})
        for each in article:
            article = each.find_all("h1", {"class": "search-result-story__headline"})[0]
            article_url = article.find("a")["href"]
            if article_url != '':
                uri = "http://www.bloomberg.com/" + article_url
                self.uris.add(uri)
            else:
                continue


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
        print json.dumps({"uri":uri})