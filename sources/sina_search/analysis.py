# encoding=utf-8
"""sina_search

hits: http://finance.sina.com.cn/stock/jsy/20141125/043020909481.shtml
"""

import json
import sys
import logging
import unittest
import requests
import os
import re
import time

from bs4 import BeautifulSoup


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")



class Analysis(object):
    
    def __init__(self, path, url=None):
        self.path = path
        self.url = url
        self.comment_id = None
        self.comment_count = None
        self.soup = None
        self.result = {}
        self.text = None
        
    def parse(self):
        if os.path.exists(self.path) is False:
            url_time = re.search(r'\d{8}', self.url)
            if url_time != None:
                self.parse_url(url_time.group(0))
                self.parse_comment_url()
                if self.comment_id != None:
                    self.parse_show_and_total()
                    self.parse_comment_contents()
                else:
                    self.result["show"] = ''
                    self.result["total"] = ''
                    self.result["comment_contents"] = ''
            else:
                self.result = {"media_name": "", "title": "", "show": "", "content": "", "time": "", "keywords": "", "total": "", "comment_contents": ""}
                return self.result
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
                self.soup = BeautifulSoup(self.text, "html5lib")
                self.result["show"] = ''
                self.result["total"] = ''
                self.result["comment_contents"] = ''

        self.parse_title()
        self.parse_time()
        self.parse_media_name()
        self.parse_keywords()
        self.parse_content()
        logging.debug("result is %s", json.dumps(self.result, indent=4))

    def parse_url(self, url_time):
        r = requests.get(self.url)
        if int(url_time) > 20121031:
            try:
                self.soup = BeautifulSoup(r.content.decode('gbk'), "html5lib")
            except:
                self.soup = BeautifulSoup(r.content, "html5lib")
        else:
            try:
                self.soup = BeautifulSoup(r.content.decode('gbk'), "html.parser")
            except:
                self.soup = BeautifulSoup(r.content, "html.parser")

    def parse_comment_url(self):
        news_id = re.search(r'\d{12}', self.url)
        if news_id == None:
            news_id = re.search(r'\d{11}', self.url)
            if news_id == None:
                self.comment_id = None
            else:
                self.comment_id = news_id.group(0)[4:11]
        else:
            self.comment_id = news_id.group(0)[4:12]

    def parse_show_and_total(self):
        jscontent = requests.get("http://comment5.news.sina.com.cn/page/info?format=js&channel=cj&newsid=31-1-" + self.comment_id +"&group=&compress=1&ie=gbk&oe=gbk&page=1&page_size=100&jsvar=requestId").content
        jscontent = jscontent.replace('var requestId=', '')
        js_dict = json.loads(jscontent)
        js_data = js_dict.get('result')
        js_count = js_data.get('count')
        try:
            self.result["show"] = js_count.get('show')
            self.result["total"] = js_count.get('total')
        except:
            self.result["show"] = ''
            self.result["total"] = ''
        self.comment_count = self.result["show"]

    def parse_comment_contents(self):
        count = 1
        self.result["comment_contents"] = {}
        for page in range(1, ((self.comment_count-1)/100)+2):
            jscontent = requests.get("http://comment5.news.sina.com.cn/page/info?format=js&channel=cj&newsid=31-1-" + self.comment_id +"&group=&compress=1&ie=gbk&oe=gbk&page=" + str(page) +"&page_size=100&jsvar=requestId").content
            jscontent = jscontent.replace('var requestId=', '')
            js_dict = json.loads(jscontent)
            js_data = js_dict.get('result')
            cmntlist = js_data.get('cmntlist')
            try:
                for each in cmntlist:
                    comment_content = each.get('content')
                    self.result["comment_contents"]["content_" + str(count)] = comment_content
                    count += 1
            except:
                time.sleep(0.01)

    def parse_title(self):
        h1 = self.soup.find("h1", {"id": "artibodyTitle"})
        if h1 != None:
            self.result["title"] = h1.get_text().strip()
        else:
            self.result["title"] = ''

    def parse_time(self):
        span = self.soup.find("span", {"id": "pub_date"})
        if span != None:
            self.result["time"] = span.get_text().strip()
        else:
            self.result["time"] = ''
    
    def parse_media_name(self):
        span = self.soup.find("span", {"id": "media_name"})
        if span != None:
            if span.a == None:
                self.result["media_name"] = span.get_text().strip()
            else:
                self.result["media_name"] = span.a.get_text().strip()
        else:
            self.result["media_name"] = ''

    def parse_keywords(self):
        keyword = ''
        p = self.soup.find("p", {"class": "art_keywords"})
        if p != None:
            p = p.find_all('a')
            for a in p:
                keyword += a.string
        self.result["keywords"] = keyword

    def parse_content(self):
        div = self.soup.find("div", {"id": "artibody"})
        content = ''
        if div != None:
            div = div.find_all('p')
            for p in div:
                if p.string == None:
                    p = self.soup.find('span')
                    for span in p:
                        try:
                            content += span.get_text()
                        except:
                            pass
                else:
                    content += p.get_text()
        self.result["content"] = content
    
    

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "5950.txt"

    def test_parse(self):
        """http://finance.sina.com.cn/stock/jsy/20141125/043020909481.shtml
        """
        self.analysis = Analysis(self.path, "http://finance.sina.com.cn/stock/jsy/20141125/043020909481.shtml")
        self.analysis.parse()

        self.assertNotEqual(self.analysis.result, {})
        self.assertIsNotNone(self.analysis.result["title"])
        self.assertIsNotNone(self.analysis.result["time"])
        self.assertIsNotNone(self.analysis.result["media_name"])
        self.assertIsNotNone(self.analysis.result["keywords"])
        self.assertIsNotNone(self.analysis.result["show"])
        self.assertIsNotNone(self.analysis.result["total"])
        self.assertIsNotNone(self.analysis.result["content"])
        self.assertIsNotNone(self.analysis.result["comment_contents"])



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