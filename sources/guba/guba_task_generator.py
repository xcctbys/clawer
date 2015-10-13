#encoding=utf-8


import urllib
import json
import sys
import logging
import unittest
import requests
import os

from bs4 import BeautifulSoup
import urlparse


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")




class Generator(object):
    MAX_PAGE = 21704
    HOST = "http://guba.eastmoney.com"
    
    def __init__(self):
        self.uris = set()
        self.last_page_path = "/tmp/guba_last_page"
        self.last_page = 1
        self.load_last_page()
        
    def page_url(self, page):
        return "http://guba.eastmoney.com/list,szzs,f_%d.html" % page
        
    def obtain_urls(self):
        for page in range(self.last_page, self.last_page+20):
            if page > self.MAX_PAGE:
                break
            
            self.do_obtain(page)
        
        self.last_page = page + 1
        self.save_last_page()
        
    def do_obtain(self, page):
        r = requests.get(self.page_url(page))
        if r.status_code != 200:
            return False
        
        soup = BeautifulSoup(r.text, "html.parser")
        news_container = soup.find("div", {"id":"articlelistnew"})   
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
            
    def save_last_page(self):
        with open(self.last_page_path, "w") as f:
            f.write("%d" % self.last_page)
             
    def load_last_page(self):
        if os.path.exists(self.last_page_path) is False:
            return
        with open(self.last_page_path, "r") as f:
            self.last_page = int(f.read())
        


class GeneratorTest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def test_obtain_urls(self):
        self.generator = Generator(20783)
        self.generator.obtain_urls()
        
        logging.debug("urls count is %d", len(self.generator.uris))
        
        self.assertNotEqual(self.generator.uris, [])
        self.assertEqual(len(self.generator.uris), 80)
        
        

if __name__ == "__main__":
    if DEBUG:
        unittest.main()
        
    generator = Generator()
    generator.obtain_urls()
    for uri in generator.uris:
        print json.dumps({"uri":uri, "download_engine":"phantomjs"})