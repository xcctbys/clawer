#encoding=utf-8
"""分析股吧的数据
http://guba.eastmoney.com/news,szzs,196350270.html
"""

import json
import sys
import logging
import unittest
import requests

from bs4 import BeautifulSoup


DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class Analysis(object):
    
    def __init__(self, path):
        self.path = path
        self.soup = None
        self.result = {}
        
    def parse(self):
        self.soup = BeautifulSoup(open(self.path), "html.parser")
        self.parse_read_number()
    
    def parse_read_number(self):
        div = self.soup.find("div", {"id":"zwmbtilr"})
        spans = div.find_all("span", {"class":"tc1"})
        logging.debug("div is %s, spans length is %d", div.contents, len(spans))
        read_number = int(spans[0].contents[0])
        self.result["read_number"] = read_number
        
        

class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "44599.txt"
        
    def test_parse(self):
        self.analysis = Analysis(self.path)
        self.analysis.parse()
        
        self.assertNotEqual(self.analysis.result, {})
        self.assertGreater(self.analysis.result["read_number"], 0)
            
    


if __name__ == "__main__":
    if DEBUG:
        unittest.main()
    
    in_data = sys.stdin.read()
    logging.debug("in data is: %s", in_data)
    
    in_json = json.loads(in_data)
    analysis = Analysis(in_json["path"])
    analysis.parse()
    
    print json.dumps(analysis.result)
    
    