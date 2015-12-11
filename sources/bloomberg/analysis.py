# encoding=utf-8
"""bloomberg

hits: http://www.bloomberg.com/news/articles/2015-11-11/apple-ipad-pro-review-bigger-better-
"""

import json
import sys
import logging
import unittest
import requests
import os
import datetime

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
        self.soup = None
        self.result = {}
        self.text = None

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
        self.parse_time()
        self.parse_content()
        logging.debug("result is %s", json.dumps(self.result, indent=4))

    def parse_title(self):
        h1 = self.soup.find("h1", {"class": "lede-headline"})
        if h1 != None:
            span = h1.find("span")
            self.result["title"] = span.get_text().strip()
        else:
            self.result["title"] = ''

    def parse_time(self):
        time = self.soup.find("time", {"class": "published-at time-based"})
        if time != None:
            self.result["time"] = time.get_text().strip() + " system_time:" + datetime.datetime.today().strftime("%Y-%m-%d")
        else:
            self.result["time"] = "system_time:" + datetime.datetime.today().strftime("%Y-%m-%d")

    def parse_content(self):
        div = self.soup.find("div", {"class": "article-body__content"})
        all_p = div.find_all("p")
        content = ''
        for p in all_p:
            content += p.get_text().replace("\n", "")
        self.result["content"] = content



class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "articletest.txt"

    def test_parse(self):
        """http://www.bloomberg.com/news/articles/2015-11-11/apple-ipad-pro-review-bigger-better-
        """
        self.analysis = Analysis(self.path, "http://www.bloomberg.com/news/articles/2015-11-11/"
                                            "apple-ipad-pro-review-bigger-better-")
        self.analysis.parse()
        self.assertNotEqual(self.analysis.result, {})
        self.assertIsNotNone(self.analysis.result["title"])
        self.assertIsNotNone(self.analysis.result["time"])
        self.assertIsNotNone(self.analysis.result["content"])



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