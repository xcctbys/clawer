# encoding=utf-8
""" example is http://www.live.chinacourt.org/fygg/index/kindid/6.shtml
"""

import logging
import json
import unittest
import traceback
import os
import cPickle as pickle
import datetime
import requests
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
        self.current_page = 1
        self.date_now = datetime.datetime.now()
        self.path = "/tmp/china_court_all"
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
                self.current_page = old.current_page
            else:
                self.current_page = 1

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)


class Generator(object):
    STEP = 11

    def __init__(self):
        self.uris = set()
        self.history = History()
        self.history.load()

    def obtain_urls(self):
        for i in range(1, self.STEP):
            url = "http://rmfygg.court.gov.cn/psca/lgnot/solr/searchBulletinInterface.do?callback=jQuery" \
                  "152043560746777802706_1448866417716&start=" + str(self.history.current_page) + "&limit=16&wd=rmfybulletin" \
                  "&list%5B0%5D=bltntype%3A&_=1448866625744"
            self.uris.add(url)
            self.history.current_page += 1
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

        self.assertGreater(len(self.generator.uris), 0)


if __name__ == "__main__":

    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_urls()

    for uri in generator.uris:
        print json.dumps({"uri": uri})
