#encoding=utf-8
""" example is http://paper.people.com.cn/rmrb/html/2015-11/09/nbs.D110000renmrb_01.htm
"""


import urllib
import json
import sys
import logging
import unittest
import requests
import os
import cPickle as pickle

from bs4 import BeautifulSoup
import urlparse
try:
    import pwd
except:
    pass
import traceback
import datetime


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")



class History(object):
    jishu = 1;
    def __init__(self):
        self.current_date =  datetime.date.today()
        self.total_page = 1
        self.path = "/tmp/cdh"
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
            self.jishu = old.jishu


    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)




class Generator(object):
    HOST = "http://paper.people.com.cn/"

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
        if self.history.total_page > 0:
            self.obtain_total_page(self.history.current_date)
            self.history.save()
        # 控制每次输一条
        for page in range(self.history.jishu, self.history.jishu+1):
            self.do_obtain(self.history.current_date, page)
            if self.history.jishu > self.history.total_page:
                 self.history.jishu = 0
            self.history.jishu += 1
            # print self.history.jishu
            # print self.history.total_page
        self.history.save()

    def page_url(self, dt, page):
        if page <10:
            return urlparse.urljoin(self.HOST, "/rmrb/html/%s/nbs.D110000renmrb_0%d.htm" % (dt.strftime("%Y-%m/%d"), page))
        if page>=10:
            return urlparse.urljoin(self.HOST, "/rmrb/html/%s/nbs.D110000renmrb_%d.htm" % (dt.strftime("%Y-%m/%d"), page))
    def do_obtain(self, dt, page):
        url = self.page_url(dt, page)
        r = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        if r.status_code != 200:
            return
        soup = BeautifulSoup(r.text, "html5lib")
        div = soup.find("div", {"id":"titleList"})
        # logging.debug("div is %s", div)
        links = div.find_all("a")
        for a in links:
            # logging.debug("a is %s", a)
            node_url = urlparse.urljoin(url, a["href"])
            self.uris.add(node_url)
            # logging.debug("uri is %s", node_url)
            # print json.dumps({"uri":node_url})



    def obtain_total_page(self, dt):
        url = self.page_url(dt, 1)
        r = requests.get(url)
        if r.status_code != 200:
            return False

        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a", {"id": "pageLink"})
        self.history.total_page = len(links)
        # logging.debug("%s total page is %d", url, self.history.total_page)
        return True


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()

        # logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)



if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_urls()
    for uri in generator.uris:
        print json.dumps({"uri":uri})
