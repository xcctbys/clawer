# encoding=utf-8
""" example is http://seekingalpha.com/analysis/all/all/1443809545?summaries_state
"""

import json
import logging
import unittest
import requests
import os
import time
import datetime
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



class History(object):

    def __init__(self):
        self.path = "/tmp/seekingalphaByDay"
        self.timestamp_STEP = 0
        self.date_now = datetime.datetime.now()

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
            if old.date_now.strftime("%Y-%m-%d") == self.date_now.strftime("%Y-%m-%d"):
                self.timestamp_STEP = old.timestamp_STEP
            else:
                self.timestamp_STEP = 0

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)




class Generator(object):
    HOST = 'http://seekingalpha.com/analysis/all/all/'
    articleHost = 'http://seekingalpha.com'
    dateSTEP = 21600
    timeStamp = int(time.time())

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

    def page_url(self):
        times = self.timeStamp - self.dateSTEP * self.history.timestamp_STEP
        if times <= self.timeStamp - 86400:
            return
        url = self.HOST + str(times)
        self.obtain_urls(url)
        self.history.timestamp_STEP += 1
        self.history.save()

    def obtain_urls(self, url):
        r = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        soup = BeautifulSoup(r.text, "html5lib")
        a = soup.find_all("a", {"class": "article_title"})
        for each in a:
            self.uris.add(self.articleHost + each["href"])



class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.page_url()

        logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)



if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.page_url()

    for uri in generator.uris:
        print json.dumps({"uri": uri})
