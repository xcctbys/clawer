# encoding=utf-8
""" example is http://www.twitter.com/search?q=additive+manufacturing since:2015-08-05 until:2015-08-06&src=typd
"""


import urllib
import json
import logging
import unittest
import os
import datetime
import cPickle as pickle

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
        u'additive manufacturing',
        u'rapid prototyping',
        u'3D printing',
        u'3D printer',
        u'filament',
        u'makerbot',
        u'Wearable device',
        u'Wearable smart device',
        u'Smart Bracelet',
        u'Smart Watch',
        u'big data',
        u'NoSQL database',
        u'in-memory analytics',
        u'Data Warehouse',
        u'data mining',
        u'machine learning',
        u'Genetic testing',
        u'DNA testing',
        u'DNA sequencing',
        u'Gene test',
        u'genetic diagnosis',
        u'Blood DNA test',
        u'Body fluid DNA test',
        u'Robot',
        u'Industrial Robot AI',
        u'Artificial Intelligence',
        u'factory automation',
        u'UAV',
        u'Unmanned aerial vehicle',
        u'remotely piloted aircraft',
        u'RPA',
        u'Drone revolution',
        u'Drone Delivery',
        u'Unmanned helicopter',
        u'Unmanned fixed wing aircraft',
        u'Unmanned airship',
        u'Unmanned wing aircraft',
        u'Internet of things',
        u'IoT',
        u'RFID',
        u'M2M',
        u'Internet of Everything',
        u'New Energy',
        u'alternative energy',
        u'renewable energy',
        u'clean energy',
        u'Renewable energy',
        u'Solar energy',
        u'Wind energy',
        u'Biomass energy',
        u'Hydrogenic energy',
        u'Geothermal energy',
        u'Ocean energy',
        u'Chemical energy',
        u'Nuclear energy',
        u'Mobile payment',
        u'mobile money',
        u'mobile money transfer',
        u'mobile wallet',
        u'NFC payment',
        u'QR code payments',
        u'cloud computing',
        u'cloud safety',
        u'cloud storage',
        u'IaaS',
        u'PaaS',
        u'SaaS',
        u'smart community',
        u'Smart city',
        u'Digital city',
        u'Wireless city',
        u'Mhealth',
        u'Mobile health',
        u'Mobile Healthcare',
        u'Remote patient monitoring',
        u'RPM',
        u'telehealth',
        u'eHealth',
        u'Intelligent hospital system',
        u'Regional health system',
        u'Home health system',
        u'Smart TV',
        u'connected TV',
        u'hybrid TV',
        u'set-top box',
        u'internet TV',
        u'Online interactive media',
        u'On-demanding streaming media',
        u'Smart grid',
        u'Smart Power Grids',
        u'intelligent grid',
        u'intelligent power grids',
        u'Smart home',
        u'home automation',
        u'building automation',
        u'intelligent home',
        u'E-home',
        u'digital home',
        u'home networking',
        u'Intelligent Vehicles',
        u'Intelligent driving',
        u'driverless car',
        u'self-driving car',
        u'autonomous vehicle',
        u'electric vehicles',
        u'Smart Phone',
        u'smartphone',
        u'tablet',
        u'Tablet PC',
        u'iPhone',
        u'iPad',
        u'Galaxy',
        u'Surface Tablet',
        u'Industrie 4.0',
        u'smart factory',
        u'Smart Manufacturing'

]


class History(object):

    def __init__(self):
        self.current_keyword = 0
        self.current_count = 117
        self.path = "/tmp/twitter"
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
            self.current_count = old.current_count

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)


class Generator(object):
    HOST = 'http://www.twitter.com/search?'
    STEP = 11  # 每次输出的url数量步长
    dateSTEP = 1  # 回溯的时间长度
    currentDay = datetime.datetime.now()

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
            self.page_url(keyword)
        self.history.current_count -= self.STEP
        self.history.save()

    def page_url(self, keyword):
        for i in range(0, self.dateSTEP):
            url = self.HOST + urllib.urlencode({"q": keyword.encode("utf8")}) + ' since:' + (self.currentDay - datetime.timedelta(days = i)).strftime("%Y-%m-%d") + ' until:' + (self.currentDay - datetime.timedelta(days = i - 1)).strftime("%Y-%m-%d") + '&src=typd'
            self.uris.add(url)
        self.history.current_keyword += 1
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
