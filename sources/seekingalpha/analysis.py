# encoding=utf-8
"""seekingalpha

hits: http://seekingalpha.com/article/3607276-clash-of-the-titans-qualcomm-earnings-and-beyond
"""

import json
import sys
import logging
import unittest
import requests
import os

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

        self.soup = BeautifulSoup(self.text, "html5lib")
        self.parse_title()
        self.parse_time()
        self.parse_content()
        logging.debug("result is %s", json.dumps(self.result, indent=4))

    def parse_title(self):
        h1 = self.soup.find("h1")
        if h1 != None:
            self.result["title"] = h1.get_text().strip()
        else:
            self.result["title"] = ''

    def parse_time(self):
        span = self.soup.find("span", {"itemprop": "datePublished"})
        if span != None:
            self.result["time"] = span.get_text().strip()
        else:
            self.result["time"] = ''

    def parse_content(self):
        all_p = self.soup.find_all("p")
        content = ''
        for p in all_p:
            content += p.get_text().replace("\n","")
        self.result["content"] = content



class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "test.txt"

    def test_parse(self):
        """http://seekingalpha.com/article/3607276-clash-of-the-titans-qualcomm-earnings-and-beyond
        """
        self.analysis = Analysis(self.path, "http://seekingalpha.com/article/3607276-clash-of-the-titans-qualcomm-earnings-and-beyond")
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