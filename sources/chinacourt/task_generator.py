#encoding=utf-8
""" example is http://rmfyb.chinacourt.org/paper/html/2015-08/22/node_4.htm
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
import pwd
import traceback
import datetime


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")




class History(object):
    START_DATE = datetime.datetime(2010, 1, 1)
    END_DATE = datetime.datetime.now() - datetime.timedelta(2)
    
    def __init__(self):
        self.current_date = self.START_DATE
        self.total_page = 0
        self.path = "/tmp/chinacourt"
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
            self.current_date = old.current_date

    
    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)
        



class Generator(object):
    HOST = "http://rmfyb.chinacourt.org/"
    STEP = 7
    
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
        end = self.history.current_date + datetime.timedelta(self.STEP)
        while self.history.current_date < end:
            if self.history.current_date.date() >= self.history.END_DATE.date():
                break
            
            if self.history.total_page <= 0:
                if not self.obtain_total_page(self.history.current_date):
                    self.history.current_date += datetime.timedelta(1)
                    self.history.save()
                    continue
            
            for page in range(1, self.history.total_page+1):
                self.do_obtain(self.history.current_date, page)
            
            self.history.current_date += datetime.timedelta(1)
            self.history.total_page = 0
            self.history.save()
        
    
    def page_url(self, dt, page):
        return urlparse.urljoin(self.HOST, "/paper/html/%s/node_%d.htm" % (dt.strftime("%Y-%m/%d"), page))    
    
    def do_obtain(self, dt, page):
        url = self.page_url(dt, page)
        r = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        if r.status_code != 200:
            return
        #logging.debug(u"uid %s, page %s , text %s", uid, page, r.text)
        soup = BeautifulSoup(r.text, "html5lib")
        div = soup.find("div", {"style":"height:416px; overflow-y:scroll; width:100%;"})
        logging.debug("div is %s", div)
        links = div.find_all("a")
        for a in links:
            logging.debug("a is %s", a)
            a_div = a.find("div", {"style":"display:inline"})
            if a_div and "id" in a_div.attrs and a_div["id"].find("mp") > -1:
                node_url = urlparse.urljoin(url, a["href"])
                self.uris.add(node_url)
                logging.debug("uri is %s", node_url)
        
    
    def obtain_total_page(self, dt):
        url = self.page_url(dt, 1)
        r = requests.get(url)
        if r.status_code != 200:
            return False
        
        soup = BeautifulSoup(r.text, "html5lib")
        links = soup.find_all("a", {"id": "pageLink"})
        self.history.total_page = len(links)
        
        logging.debug("%s total page is %d", url, self.history.total_page)
        return True


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