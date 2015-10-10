#encoding=utf-8
""" example is http://blog.sina.com.cn/s/articlelist_1300871220_0_1.html
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


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


Enterprises = [
    {"name": u"安信证券股份有限公司北京分公司", "reg_id":"a1a1a1a021ced5020121e19fc345143e", "reg_no":"110102012003809", }
] 



class Generator(object):
    HOST = "http://qyxy.baic.gov.cn/"
    STEP = 100
    
    def __init__(self):
        self.uris = set()
        self.history = History()
        self.history_path = "/tmp/sina_blog"
        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))
        self.load_history()
            
    def page_url(self, uid, page):
        return urlparse.urljoin(self.HOST, "/s/articlelist_%d_0_%d.html" % (uid, page))
        
    def obtain_urls(self):
        for page in range(self.history.current_page+1, self.history.current_page+1+self.STEP):
            if self.history.total_page > 0 and page > self.history.total_page:
                self.history.position += 1
                if self.history.position > len(TOP_100_IDS):
                    break
                self.history.uid = TOP_100_IDS[self.history.position]
                self.history.current_page = 0
                self.history.total_page = 0
                break
                
            self.do_obtain(self.history.uid, page)
        
        self.history.current_page = page
        self.save_history()
        
    def do_obtain(self, uid, page):
        r = requests.get(self.page_url(uid, page), headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        #logging.debug(u"uid %s, page %s , text %s", uid, page, r.text)
        soup = BeautifulSoup(r.text, "html5lib")
        
        if self.history.total_page <= 0:
            self.history.total_page = self.parse_total_page(soup)
        
        div = soup.find("div", {"class":"articleList"})
        spans = div.find_all("span", {"class":"atc_title"})
        for span in spans:
            self.uris.add(span.a["href"])
        
        return True
        
    
    def parse_total_page(self, soup):
        ul = soup.find("ul", {"class":"SG_pages"})
        logging.debug(u"ul is %s", ul)
        span = ul.find("span")
        logging.debug(u"span is %s", span)
        total = int(filter(str.isdigit, span.get_text().encode("utf-8")))
        return total
        
         


class GeneratorTest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()
        
        logging.debug("urls count is %d", len(self.generator.uris))
        
        self.assertGreater(len(self.generator.uris), 0)
        self.assertGreater(self.generator.history.position, 0)
        
        

if __name__ == "__main__":
    if DEBUG:
        unittest.main()
        
    generator = Generator()
    generator.obtain_urls()
    for uri in generator.uris:
        print json.dumps({"uri":uri})