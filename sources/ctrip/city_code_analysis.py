#encoding=utf-8
"""分析国内的所有城市三字码
http://airport.supfree.net/index.asp?page=284
"""

import urllib
import json
import sys
import logging
import unittest

from bs4 import BeautifulSoup


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class Analysis(object):
    
    def __init__(self, path):
        self.path = path
        self.soup = None
        self.result = {"city_codes":[]}
        
    def parse(self):
        self.soup = BeautifulSoup(open(self.path), "html.parser")
        table = self.soup.find("table")
        logging.debug("table is: %s, children count is %d", table, len(table.contents))
        
        trs = table.find_all("tr")
        logging.debug("tr count %d", len(trs))
        
        for tr in trs:
            if "class" in tr.attrs and tr["class"][0] == "xctd":
                continue
            
            tds = tr.find_all("td")
            logging.debug("tr %s, td count %d", tr, len(tds))
            
            city = tds[0].span.contents
            three_code = tds[1].contents
            four_code = tds[2].contents
            airport = tds[3].contents
            english_city = tds[4].contents
            self.result["city_codes"].append({"city":city, "three_code":three_code, "four_code":four_code, "airport":airport, "english_city":english_city})
        

class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "2276.txt"
        
    def test_parse(self):
        self.analysis = Analysis(self.path)
        self.analysis.parse()
        
        self.assertNotEqual(self.analysis.result, {})
        
        
    


if __name__ == "__main__":
    if DEBUG:
        unittest.main()
    
    in_data = sys.stdin.read()
    logging.debug("in data is: %s", in_data)
    
    in_json = json.loads(in_data)
    analysis = Analysis(in_json["path"])
    analysis.parse()
    
    print json.dumps(analysis.result)
    
    