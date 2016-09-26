# encoding=utf-8
"""

http://paper.people.com.cn/rmrb/html/2015-01/01/nw.D110000renmrb_20150101_1-01.htm"
"""

import json
import sys
import logging
import unittest
import requests
import os
import re
import codecs
import pickle

reload(sys)
sys.setdefaultencoding('utf8')

from bs4 import BeautifulSoup

DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

keyword_list = ["宏观", "经济", "GDP", "投资", "消费", "出口", "贸易", "产业", "房地产", "金融", "股市", "就业", "物价", "收入",
                "利率", "央行", "不确定","政策"]
"""
文章发布时间,文章标题,文章内容,符合的关键词,版面数,是否有附图
"""


class Analysis(object):
    def __init__(self, path, keyword_list=keyword_list, url=None):
        self.path = path
        self.url = url
        self.soup = None
        self.result = {}
        self.text = None
        self.keyword_list = keyword_list
        self.total_page = 0

    def parse(self):
        if os.path.exists(self.path) is False:
            r = requests.get(self.url)
            self.text = r.content
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
                if self.text == '':
                    r = requests.get(self.url)
                    self.text = r.content

        self.soup = BeautifulSoup(self.text, "html5lib")
        self.parse_title()
        self.parse_time_page()
        self.parse_content()
        self.parse_keyword()
        self.parse_img()
        logging.debug("result is %s", json.dumps(self.result, indent=4))

    def parse_title(self):
        h1 = self.soup.find("h1")
        if h1 != None:
            self.result["title"] = h1.get_text().strip()
        else:
            self.result["title"] = ''

    def parse_time_page(self):
        # span = self.soup.find("div", {"id": "riqi_"})
        span = self.soup.find("div", {"class": "lai"})
        if span != None:
            time = span.get_text().strip()
            m = re.search(ur'[\(（][\s\S]*[\)）]', time).group()
            par_list =re.split(ur'[\(,（,\s]\s*', m)
            datetime = par_list[1]
            page = par_list[3]
            self.result["time"] = str(datetime)
            self.result["pageID"] = page
            # s = time.replace(u"人民日报", "")
            # self.result["time"] = str(s.lstrip())
        else:
            self.result["time"] = ''

    def parse_content(self):
        articleContent = self.soup.find("div", {"id": "articleContent"})
        content = ''
        try:
            all_p = articleContent.find_all("p")

            for p in all_p:
                content += p.get_text().replace("\n", "")
        except:
            pass
        self.result["content"] = content

    def parse_keyword(self):
        match_list = []
        for keyword in keyword_list:
            keyword = str.decode(keyword, 'utf-8')
            if re.search(keyword, self.result["content"]):
                key = re.search(keyword, self.result["content"]).group()
                match_list.append(key)
        self.result["match_keyword"] = match_list

    def parse_img(self):
        host = "http://paper.people.com.cn/rmrb"
        self.result["img"] = {"exist": "no", "img_uri": []}
        img_uri = self.soup.find_all("table", {"class": "pci_c"})

        if img_uri:
            self.result["img"]["exist"] = "yes"
            uri_list = []
            for uri in img_uri:
                uri = uri.find('img').get('src', '')
                uri = uri.replace("../../..", "")
                uri = host + uri
                uri_list.append(uri)
            self.result["img"]["img_uri"] = uri_list
        else:
            pass

    def page_url(self, dt, page):
        if page < 10:
            return urlparse.urljoin(self.HOST,
                                    "/rmrb/html/%s/nbs.D110000renmrb_0%d.htm" % (dt.strftime("%Y-%m/%d"), page))
        else:
            return urlparse.urljoin(self.HOST,
                                    "/rmrb/html/%s/nbs.D110000renmrb_%d.htm" % (dt.strftime("%Y-%m/%d"), page))


if __name__ == "__main__":
    if DEBUG:
        unittest.main()
    in_data = sys.stdin.read()
    in_json = json.loads(in_data)
    url = in_json.get("url")
    analysis = Analysis(in_json["path"], url)
    analysis.parse()
    print json.dumps(analysis.result)