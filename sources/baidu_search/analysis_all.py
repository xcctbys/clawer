# encoding=utf-8
"""china court

hits: http://wo.cs.com.cn/html/2012-11/24/content_461302.htm?div=-1
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
        self.div = None
        self.text = None
        self.soup = None

    def parse(self):
        if os.path.exists(self.path) is False:
            r = requests.get(self.url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
            self.text = r.content
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
        self.soup = BeautifulSoup(self.text, "html5lib")
        html_content = self.soup.find("html")

        self.result["html"] = str(html_content)
        logging.debug("result is %s", json.dumps(self.result, indent=4))


class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "test.txt"

    def test_parse(self):
        """http://wo.cs.com.cn/html/2012-11/24/content_461302.htm?div=-1
        """
        self.analysis = Analysis(self.path, "http://wo.cs.com.cn/html/2012-11/24/content_461302.htm?div=-1")
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
