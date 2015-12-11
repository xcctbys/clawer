# encoding=utf-8
""" example is http://www.bloomberg.com/search?query=China+Stock
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
        'China Stock',
        'Chinese Stock',
]



class History(object):

    def __init__(self):
        self.current_keyword = 0
        self.current_count = 3
        self.current_time = datetime.datetime.now()
        self.path = "/tmp/bloombergCS"
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
            if old.current_time.strftime("%Y-%m-%d") == self.current_time.strftime("%Y-%m-%d"):
                self.current_keyword = old.current_keyword
                self.current_count = old.current_count
            else:
                self.current_keyword = 0
                self.current_count = 3

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)



class Generator(object):
    HOST = 'http://www.bloomberg.com/search?'
    STEP = 2
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
        if self.history.current_count <= 1:
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