#encoding=utf-8
""" example is http://www.zhihu.com/r/search?q=%E7%95%AA%E8%8C%84%E5%B7%A5%E4%BD%9C%E6%B3%95&range=&type=question&offset=20
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
    KEYWORDS = [
        u"番茄工作法",
        u"时间管理",
        u"时间管理软件",
        u"高效工作",
        u"高效学习",
        u"注意力",
        u"效率",
        u"专注",
        u"自我管理",
        u"学习",
    ]
    
    def __init__(self):
        self.position = 0
        self.page_offset = 0
        self.path = "/tmp/zhihu_new"
    
    def load(self):
        if os.path.exists(self.path) is False:
            return
        
        with open(self.path, "r") as f:
            old = pickle.load(f)
            self.position = old.position
            self.page_offset = old.page_offset

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            
    def current_keyword(self):
        if self.position >= len(self.KEYWORDS):
            return None
        return self.KEYWORDS[self.position]
        



class Generator(object):
    HOST = "http://www.zhihu.com/"
    STEP = 1
    
    def __init__(self):
        self.uris = set()
        self.history = History()
        self.history.load()
        
    def obtain_urls(self):
        if self.history.position >= len(self.history.KEYWORDS):
            self.history.position = 0
            self.history.page_offset = 0
            self.history.save()
        start = self.history.position
        end = start + self.STEP
        if end >= len(self.history.KEYWORDS):
            end = len(self.history.KEYWORDS)
            
        for _ in range(start, end+1):
            while True:
                url = self.page_url()
                if not self.do_obtain(url):
                    break

            
    def page_url(self):
        qs = urllib.urlencode({
            "type":"question",
            "q": self.history.current_keyword().encode("utf-8"),
            "range": "",
            "offset": self.history.page_offset,
        })
        return urlparse.urljoin(self.HOST, "/r/search?%s" % qs)    
    
    def do_obtain(self, url):
        resp = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        if resp.status_code != 200:
            return False
        
        data = resp.json()
        #parse all nodes
        for node in data["htmls"]:
            bs = BeautifulSoup(node)#, "html5lib")
            div = bs.find("div", {"class":"title"})
            a = div.find("a", {"class":"question-link"})
            link = urlparse.urljoin(self.HOST, a["href"])
            self.uris.add(link)
        
        if data["paging"]["next"] == None:
            self.history.page_offset = 0
            self.history.position += 1
            self.history.save() 
            return False
        
        self.history.page_offset += 10
        self.history.save()
        
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
