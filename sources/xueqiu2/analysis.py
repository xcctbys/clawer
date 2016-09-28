#encoding=utf-8
"""china court

hits: http://xueqiu.com/statuses/search.json?page=1&q=3D%E6%89%93%E5%8D%B0&_=1445322237058
"""

import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
import unittest
import requests
import os
import re
import datetime


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
        self.soup = None
        self.result = {}
        self.list = []
        self.js_article = None
        self.text = None
        self.js_list = None
        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})


    def parse(self):
        # if os.path.exists(self.path) is False:
        #     self.reqst.get('http://www.xueqiu.com') #有cookie，得先请求主页面。
        #     # print self.url
        #     r = self.reqst.get(self.url)
        #     self.text = r.text
        # else:
        #     with open(self.path, "r") as f:
        #         self.text = f.read()
        # print self.text
        self.reqst.get('https://xueqiu.com/')
        r = self.reqst.get(self.url)
        self.text = r.text
        js_dict = json.loads(self.text)
        js_list = js_dict.get("list")
        for article in js_list:
            new_a = {}
            self.js_article = article
            self.parse_title(new_a)
            self.parse_content(new_a)
            self.parse_add_datetime(new_a)
            self.list.append(new_a)
        self.result["list"] = self.list
        logging.debug("result is %s", json.dumps(self.result, indent=4))


    def parse_title(self, new_a):
        title = self.js_article.get("title")
        new_a["title"] = title

    def parse_content(self, new_a):
        content = self.js_article.get("text")
        content = re.sub("<[^>]*>", "", content).replace(" ", "")
        new_a["content"] = content.strip()

    def parse_add_datetime(self, new_a):
        time = self.js_article.get("timeBefore") + " system_time:" + datetime.datetime.today().strftime("%Y-%m-%d")
        new_a["add_datetime"] = time.strip()



class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "test.txt"

    def test_parse(self):
        """http://xueqiu.com/statuses/search.json?page=1&q=3D%E6%89%93%E5%8D%B0&_=1445322237058,
        http://xueqiu.com/statuses/search.json?page=1&q=3D%E6%89%93%E5%8D%B0
        """

        self.analysis = Analysis(self.path, "http://xueqiu.com/statuses/search.json?page=2&q=3D%E6%89%93%E5%8D%B0")
        self.analysis.parse()

        self.assertNotEqual(self.analysis.result, [])


if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    in_data = sys.stdin.read()
    logging.debug("in data is: %s", in_data)

    in_json = json.loads(in_data)
    url = in_json.get("url")+'&_=1445322237058'
    analysis = Analysis(in_json["path"], url)
    analysis.parse()

    print json.dumps(analysis.result)