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
import codecs
import urllib
import pickle
import codecs

reload(sys)   
sys.setdefaultencoding('utf8')  

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
        self.soup = None
        self.result = {}
        self.text = None

    def parse(self):
        # if os.path.exists(self.path) is False:
        #     r = requests.get(self.url)
        #     self.text = r.content
        # else:
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
        h1 = self.soup.find("h1")
        if h1 != None:
            self.result["title"] = h1.get_text().strip()
        else:
            self.result["title"] = ''

    def parse_time(self):
        # span = self.soup.find("div", {"style":"padding-top:5px;"},{"class":"lai"})
        span = self.soup.find("div",{"id":"riqi_"})
        if span != None:
           
            time = span.get_text().strip()
            self.result["time"] = str(time).replace(u"人民日报","")
            
        else:
            self.result["time"] = ''

    def parse_content(self):
        articleContent = self.soup.find("div", {"id":"articleContent"})
        content = ''
        try:
            all_p = articleContent.find_all("p")
        
            for p in all_p:
                content += p.get_text().replace("\n", "")
        except:
            pass     
        self.result["content"] = content

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        

    def test_parse(self):
        """http://paper.people.com.cn/rmrb/html
        """
        for filenname in os.listdir(r'content/'):
            # pass
            # print filenname 
            self.path = "%s%s" % ("content/", filenname)

            self.analysis = Analysis(self.path, ",,,,,,")
            self.analysis.parse()
            self.assertNotEqual(self.analysis.result, {})
            self.assertIsNotNone(self.analysis.result["title"])
            self.assertIsNotNone(self.analysis.result["time"])
            self.assertIsNotNone(self.analysis.result["content"])


            json_name = json.dumps(self.analysis.result).decode("utf8")
           
            n = filenname.split("_")[0]
            path2 = "%s%s%s" % ('json/', n, ".json")

            write_type = 'a'
            with codecs.open(path2, write_type, 'utf-8') as f:
                f.write(json.dumps(self.analysis.result, ensure_ascii=False)+'\n')
        



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
    