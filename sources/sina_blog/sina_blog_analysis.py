#encoding=utf-8
"""sina blog analysis
http://blog.sina.com.cn/s/blog_4d89b8340102w2ej.html

hits: http://comet.blog.sina.com.cn/api?maintype=hits&act=4&aid=4d89b8340102w2ej&ref=&varname=requestId_31617693


"""

import json
import sys
import logging
import unittest
import requests
import os

from bs4 import BeautifulSoup


DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class Analysis(object):
    
    def __init__(self, path, url=None):
        self.path = path
        self.url = url
        self.soup = None
        self.result = {}
        self.text = None
        
    def parse(self):
        if os.path.exists(self.path) is False:
            r = requests.get(self.url)
            self.text = r.text
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
                
        self.soup = BeautifulSoup(self.text, "html5lib")
        self.parse_uid()
        self.parse_title()
        self.parse_content()
        self.parse_tags()
        self.parse_add_datetime()
        self.parse_comment_number()
        self.parse_read_number()
        self.parse_favorite_number()
        self.parse_forward_number()
        logging.debug("result is %s", json.dumps(self.result, indent=4))
        
    def parse_uid(self):
        span = self.soup.find("span", {"class":"last"})
        logging.debug("span is %s", span)
        a = span.find("a")
        tmps = a["href"].split("_")
        self.result["uid"] = int(filter(str.isdigit, tmps[1].encode("utf-8")))
        
    def parse_title(self):
        h2 = self.soup.find("h2", {"class":"titName SG_txta"})
        title = h2.get_text()
        self.result["title"] = title.strip()
            
    def parse_content(self):
        div = self.soup.find("div", {"id":"sina_keyword_ad_area2"})
        self.result["content"] = div.get_text().strip()
    
    def parse_tags(self):
        td = self.soup.find("td", {"class":"blog_tag"})
        self.result["tags"] = []
        h3s = td.find_all("h3")
        for h3 in h3s:
            self.result["tags"].append(h3.get_text().strip())
    
    def parse_add_datetime(self):
        span = self.soup.find("span", {"class":"time SG_txtc"})
        self.result["add_datetime"] = span.get_text().strip("()") 
    
    def parse_comment_number(self):
        pass
    
    def parse_read_number(self):
        div = self.soup.find("div", {"class":"IL"})
        hashid = self.url.split("_")[1].split(".")[0]
        span = div.find("span", {"id":"r_%s" % hashid})
        logging.debug("hashid %s, span %s", hashid, span)
        self.result["read_number"] = span.get_text().strip("()")
    
    def parse_favorite_number(self):
        div = self.soup.find("div", {"class":"IL"})
        hashid = self.url.split("_")[1].split(".")[0]
        span = div.find("span", {"id":"f_%s" % hashid})
        logging.debug("hashid %s, span %s", hashid, span)
        self.result["favorite_number"] = span.get_text().strip("()")
    
    def parse_forward_number(self):
        div = self.soup.find("div", {"class":"IL"})
        hashid = self.url.split("_")[1].split(".")[0]
        a = div.find("a", {"id":"z_%s" % hashid})
        logging.debug("hashid %s, a %s", hashid, a)
        self.result["forward_number"] = a.get_text().strip("()")
    

class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "595050.txt"
        
    def test_parse(self):
        """http://blog.sina.com.cn/s/blog_4d89b8340102w2ej.html
        """
        self.analysis = Analysis(self.path, "http://blog.sina.com.cn/s/blog_4d89b8340102w2ej.html")
        self.analysis.parse()
        
        self.assertNotEqual(self.analysis.result, {})
        self.assertEqual(self.analysis.result["uid"], 1300871220)
        self.assertIsNotNone(self.analysis.result["title"])
        self.assertIsNotNone(self.analysis.result["content"])
        self.assertGreater(len(self.analysis.result["tags"]), 0)
        self.assertIsNotNone(self.analysis.result["add_datetime"])
        self.assertGreater(self.analysis.result["read_number"], 0)
    


if __name__ == "__main__":
    if DEBUG:
        unittest.main()
    
    in_data = sys.stdin.read()
    logging.debug("in data is: %s", in_data)
    
    in_json = json.loads(in_data)
    url = in_json.get("url")
    analysis = Analysis(in_json["path"], url)
    analysis.parse()
    
    print json.dumps(analysis.result)
    
    