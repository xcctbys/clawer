# encoding=utf-8


import json
import logging
import unittest
import requests
import os
import traceback
import pwd
import cPickle
import datetime

from bs4 import BeautifulSoup
import urlparse


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class History(object):
    def __init__(self):
        self.date_now = datetime.datetime.now()
        self.current_page = 1
        self.path = "/tmp/gubaByDay"
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
            old = cPickle.load(f)
            if old.date_now.strftime("%Y-%m-%d") == self.date_now.strftime("%Y-%m-%d"):
                self.current_page = old.current_page
            else:
                self.date_now = datetime.datetime.now()
                self.current_page = 1
    
    def save(self):
        with open(self.path, "w") as f:
            cPickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)


class Generator(object):
    HOST = "http://guba.eastmoney.com"
    
    def __init__(self):
        self.uris = set()
        self.history = History()
        self.history.load()
        self.step = 5

    def page_url(self, page):
        return "http://guba.eastmoney.com/list,szzs,f_%d.html" % page
        
    def obtain_urls(self):
        if self.history.current_page > 40:
            return
        end = self.history.current_page + self.step
        while self.history.current_page < end:
            self.do_obtain(self.history.current_page)
        
            self.history.current_page += 1
            self.history.save()
        
    def do_obtain(self, page):
        r = requests.get(self.page_url(page))
        if r.status_code != 200:
            return False
        
        soup = BeautifulSoup(r.text, "html.parser")
        news_container = soup.find("div", {"id": "articlelistnew"})
        divs = news_container.find_all("div")
        
        for div in divs:
            if "class" in div.attrs and "dheader" == div["class"][0]:
                continue
            
            spans = div.find_all("span")
            logging.debug("spans count is %d", len(spans))
            if len(spans) != 7:
                continue
            url_span = spans[2]
            logging.debug("url span is %s", url_span)
            url = url_span.a["href"]
            self.uris.add(urlparse.urljoin(self.HOST, url))
        
        return True


class GeneratorTest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()
        
        logging.debug("urls count is %d", len(self.generator.uris))
        
        self.assertNotEqual(self.generator.uris, [])
        self.assertGreater(len(self.generator.uris), 80)

if __name__ == "__main__":
    if DEBUG:
        unittest.main()
        
    generator = Generator()
    generator.obtain_urls()
    for uri in generator.uris:
        print json.dumps({"uri": uri, "download_engine": "phantomjs"})
