#-*- coding:UTF-8 -*-

import requests
import bs4
import re
import logging
import Queue
import multiprocessing
import  sys
import urllib
from bs4 import BeautifulSoup
import unittest
import os
import pandas as pd


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")



class  Spider(object):
	
    def __init__(self, keywords_path):
        self.keywords_path = keywords_path
        self.query_url = "http://report.bbdservice.com/show/searchCompany.do"
        self.output_path = "enterprise.csv"
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
        }
        self.keywords = []
        self.output_keywords = []
        self.result = [] #{'name':'', 'no':'', 'where':''}
        self.timeout = 90
        
    def transform(self):
        self._load_keywords()
        self._load_output()
        
        i = 0
        for keyword in self.keywords:
            if keyword in self.output_keywords:
                continue
            
            is_ok = True
            
            try:
                self._parse(keyword)
            except:
                is_ok = False
                
            i += 1
            logging.error(u"index %d, keyword %s, %s", i, keyword, is_ok)
            
        self._to_csv()
                    
    def _to_csv(self):
        dataset = [(x["name"].encode("utf-8"), x['no'], x["where"].encode("utf-8"), x["fund"].encode("utf-8")) for x in self.result]
        df = pd.DataFrame(data=dataset, columns=["name", "no", "where", "fund"])
        df.to_csv(self.output_path, mode="a", index=False)
        
    def _load_keywords(self):
        with open(self.keywords_path) as f:
            for line in f:
                line = unicode(line.strip(), "utf-8")
                self.keywords.append(line)
                
    def _load_output(self):
        if os.path.exists(self.output_path) is False:
            return
        
        with open(self.output_path) as f:
            for line in f:
                keyword = line.split(",")[0].strip()
                self.output_keywords.append(unicode(keyword, "utf-8"))
        
        self.output_keywords = list(set(self.output_keywords))
                
    def _parse(self, keyword):
        url = "%s?%s" % (self.query_url, urllib.urlencode({"term": keyword.encode("utf-8")}))
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        if r.status_code != 200:
            logging.warn("request %s, return code %d", url, r.status_code)
            return
        
        data = {"name":"", "no":"", "where":"", "fund":""}
        soup = BeautifulSoup(r.text, "html5lib")
        div = soup.find("div", {"class":"search-r fl p20 pl40 w60p"})
        ul = div.find("ul")
        lis = ul.find_all("li")
        for li in lis:
            h4 = li.find("h4")
            if not h4:
                #logging.debug("not found h4")
                continue
            title = h4.get_text().strip().strip("\"")
            if title != keyword:
                #logging.debug(u"title %s != %s", title, keyword)
                continue
            data["name"] = title
            p = li.find("p", {"class":"colorText4 f12"})
            content = p.get_text().strip()
            kvs = content.split(" ")
            for kv in kvs:
                if not kv.strip():
                    continue
                if kv.find(u"注册号：") > -1:
                    data["no"] = kv.split(u"：")[1].strip()
                if kv.find(u"住所：") > -1:
                    data["where"] = kv.split(u"：")[1].strip().replace(",", " ")
                if kv.find(u"注册资本：") > -1:
                    data["fund"] = self._clear_fund(kv.split(u"：")[1].strip().replace(",", " "))
            
            break
        
        logging.debug("data is %s", data)  
        self.result.append(data)
        
    def _clear_fund(self, fund):
        data = ""
        for c in fund:
            if c.isnumeric():
                data += c
        return int(data)
        
        
class TestSpider(unittest.TestCase):
    
    def test_transform(self):
        spider = Spider("test.txt")
        spider.transform()
        self.assertEqual(len(spider.result), 1)


if __name__ == "__main__":
    if DEBUG:
        unittest.main()
        
    spider = Spider("company_bonds.txt")
    spider.transform()

