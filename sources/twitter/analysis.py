# encoding=utf-8
"""twitter

hits: http://www.twitter.com/search?q=additive+manufacturing since:2015-11-05 until:2015-11-06&src=typd
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
        self.result = {"twitter": []}
        self.text = None

    def parse(self):
        if os.path.exists(self.path) is False:
            return
        else:
            with open(self.path, "r") as f:
                self.text = f.read()

        self.soup = BeautifulSoup(self.text, "html5lib")
        self.twitter()
        logging.debug("result is %s", json.dumps(self.result, indent=4))

    def twitter(self):
        content = self.soup.find_all("div", {"class": "content"})
        if content != None:
            for each in content:
                data = {}
                time = each.find("a", {"class": "tweet-timestamp"})
                if time != None:
                    data["time"] = time['title']
                else:
                    data["time"] = ''
                twitter = each.find("p", {"class": "js-tweet-text"})
                if twitter != None:
                    data["twitter"] = twitter.text
                else:
                    data["twitter"] = ''
                self.result["twitter"].append(data)



class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "test.txt"

    def test_parse(self):
        """http://www.twitter.com/search?q=additive+manufacturing since:2015-11-05 until:2015-11-06&src=typd
        """
        self.analysis = Analysis(self.path, "http://www.twitter.com/search?q=additive+manufacturing"
                                            " since:2015-11-05 until:2015-11-06&src=typd")
        self.analysis.parse()
        self.assertNotEqual(self.analysis.result, {})
        self.assertIsNotNone(self.analysis.result["twitter"])



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