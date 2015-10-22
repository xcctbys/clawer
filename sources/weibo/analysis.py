#encoding=utf-8
"""weibo analysis

http://m.weibo.cn/page/pageJson?queryVal=MacBook&ext=&uicode=10000011&v_p=11&containerid=100103type%3D1%26q%3DMacBook&fid=100103type%3D1%26q%3DMacBook&type=all&page=60
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
        self.result = {}
        self.text = None
        
    def parse(self):
        if os.path.exists(self.path) is False:
            r = requests.get(self.url)
            self.text = r.text
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
                
        self.result["blogs"] = []
                
        js = json.loads(self.text)
        for card in js["cards"]:
            if card["card_type"] != 11:
                continue
            for card_group in card["card_group"]:
                if card_group["card_type"] != "9":
                    continue
                blog = card_group["mblog"]
                new_blog = {}
                new_blog["id"] = blog["id"]
                new_blog["text"] = BeautifulSoup(blog["text"], "html5lib").get_text()
                new_blog["timestamp"] = blog["created_timestamp"]
                self.result["blogs"].append(new_blog)
                
        logging.debug("result is %s", json.dumps(self.result, indent=4))
        
        
class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "595050.txt"
        
    def test_parse(self):
        """request it and parse
        """
        self.analysis = Analysis(self.path, "http://m.weibo.cn/page/pageJson?containerid=&containerid=100103type%3D1%26q%3D3D+%E6%89%93%E5%8D%B0&type=all&queryVal=3D+%E6%89%93%E5%8D%B0&luicode=10000011&lfid=100103type%3D42%26q%3D%E4%BD%A0%E5%A5%BD%26t%3D&title=3D+%E6%89%93%E5%8D%B0&v_p=11&ext=&fid=100103type%3D1%26q%3D3D+%E6%89%93%E5%8D%B0&uicode=10000011&page=2")
        self.analysis.parse()
        
        self.assertEqual(len(self.analysis.result["blogs"]), 10)
    


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
    
    