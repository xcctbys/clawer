# encoding=utf-8
"""china court

hits: https://www.baidu.com/s?wd=%C9%CF%BA%A3%CD%F2%D2%B5%C6%F3%D2%B5%B9%C9%B7%DD%D3%D0%CF%DE%B9
%AB%CB%BE+%BE%C0%B7%D7&pn=0
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
        self.result = {}
        self.list = []
        self.div = None
        self.text = None
        self.soup = None

    def parse(self):
        if os.path.exists(self.path) is False:
            r = requests.get(self.url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
            self.text = r.text
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
        self.soup = BeautifulSoup(self.text, "html5lib")
        contents = self.soup.find("div", {"id": "content_left"})
        divs = contents.find_all("div", {"class": "result"})

        for div in divs:
            new_a = {}
            self.div = div
            self.parse_title(new_a)
            self.parse_url(new_a)
            self.content(new_a)
            self.list.append(new_a)
        self.result["list"] = self.list
        logging.debug("result is %s", json.dumps(self.result, indent=4))

    def parse_title(self, new_a):
        title = self.div.h3.text
        new_a["title"] = title

    def parse_url(self, new_a):
        uri = self.div.h3.a["href"]
        try:
            new_a["url"] = requests.get(uri, timeout=5).url
        except:
            new_a["url"] = ""

    def content(self, new_a):
        time = self.div.find("div", {"class": "c-abstract"}).text
        new_a["content"] = time.strip()


class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "test.txt"

    def test_parse(self):
        """https://www.baidu.com/s?wd=%C9%CF%BA%A3%CD%F2%D2%B5%C6%F3%D2%B5%B9%C9%B7%DD%D3%D0%CF%DE%B9%AB%CB%BE+%BE%C0%B7%D7&pn=0
        """
        self.analysis = Analysis(self.path, "https://www.baidu.com/s?wd=%C9%CF%BA%A3%CD%F2%D2%B5%C6%F3%D2%B5%B9%C9%B7%"
                                            "DD%D3%D0%CF%DE%B9%AB%CB%BE+%BE%C0%B7%D7&pn=0")
        self.analysis.parse()

        self.assertNotEqual(self.analysis.result, [])


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
