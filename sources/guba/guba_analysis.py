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
    
    def __init__(self, path, url=None):
        self.path = path
        self.url = url
        self.soup = None
        self.result = {}
        
    def parse(self):
        self.soup = BeautifulSoup(open(self.path), "html.parser")
        self.parse_read_number()
        self.parse_comment_number()
        self.parse_title()
        self.parse_content()
        self.parse_nickname()
        self.parse_uid()
        self.parse_influence()
        self.parse_age()
        self.parse_is_authorize()
        self.parse_add_datetime()
        self.parse_topicid()
        self.parse_comment()
        
        logging.debug("result is %s", json.dumps(self.result, indent=4))
        
    
    def parse_read_number(self):
        div = self.soup.find("div", {"id":"zwmbtilr"})
        spans = div.find_all("span", {"class":"tc1"})
        
        read_number = int(spans[0].contents[0])
        self.result["read_number"] = read_number
        
    def parse_comment_number(self):
        div = self.soup.find("div", {"id":"zwmbtilr"})
        spans = div.find_all("span", {"class":"tc1"})
        
        comment_number = int(spans[1].contents[0])
        self.result["comment_number"] = comment_number
        
    def parse_title(self):
        div = self.soup.find("div", {"id":"zwconttbt"})
        self.result["title"] = div.contents[0]
        
    def parse_content(self):
        div = self.soup.find("div", {"id":"zwconbody"})
        content_div = div.find("div", {"class":"stockcodec"})
        #logging.debug("content div is %s", content_div)
        content = u"%s" % content_div.contents
        content = content.replace("<br>", "\n").replace("</br>", "\n").strip(" u'[]")
        self.result["content"] = content
        
    def parse_nickname(self):
        div = self.soup.find("div", {"id":"zwconttbn"})
        strong = div.strong
        
        if strong.find("a"):
            self.result["nickname"] = strong.a.contents[0]
        elif strong.find("span"):
            self.result["nickname"] = strong.span.contents[0]
        else:
            self.result["nickname"] = None
    
    def parse_uid(self):
        div = self.soup.find("div", {"id":"zwconttbn"})
        span = div.find("span", {"class":"influence"})
        if not span:
            self.result["uid"] = None
            return
        self.result["uid"] = span.attrs["data-uid"]
    
    def parse_influence(self):
        div = self.soup.find("div", {"id":"zwconttbn"})
        span = div.find("span", {"class":"influence"})
        if not span:
            self.result["influence"] = None
            return
        children_span = span.find_all("span")
        if len(children_span) != 2:
            self.result["influence"] = None
            return
        self.result["influence"] = children_span[0]["class"]
        
    def parse_age(self):
        div = self.soup.find("div", {"id":"zwconttbn"})
        span = div.find("span", {"class":"influence"})
        if not span:
            self.result["age"] = None
            return
        children_span = span.find_all("span")
        if len(children_span) != 2:
            self.result["age"] = None
            return
        self.result["age"] = children_span[1].contents[0]
            
    def parse_is_authorize(self):
        div = self.soup.find("div", {"id":"zwcontent", "class":"zwgudong"})
        if not div:
            self.result["is_authorize"] = False
            return
        self.result["is_authorize"] = True
        
    def parse_add_datetime(self):
        div = self.soup.find("div", {"id":"zwconttb"})
        time_div = div.find("div", {"class":"zwfbtime"})
        tmps = time_div.contents[0].split(" ")
        self.result["add_datetime"] = "%s %s" % (tmps[1], tmps[2])
        
    def parse_topicid(self):
        if not self.url:
            self.result["topicid"] = None
            return
        
        tmps = self.url.split(",")
        src = tmps[2]
        self.result["topicid"] = src.split(".")[0]
        
    def parse_comment(self):
        self.result["comments"] = []
        container = self.soup.find("div", {"id":"zwlist"})
        comment_divs = container.find_all("div", {"class":"zwli clearfix"})
        
        if not comment_divs:
            return
        
        for div in comment_divs:
            comment = {}
            #comment id
            comment["id"] = div["id"].strip("zwli ")
            #parse name and uid
            name_span = div.find("span", {"class":"zwnick"})
            if name_span:
                a = name_span.find("a")
                if a:
                    comment["username"] = a.contents[0]
                    comment["uid"] = a["data-popper"]
            #parse influence
            influence_span = div.find("span", {"class":"influence"})
            if influence_span:
                spans = influence_span.find_all("span")
                if len(spans) == 2:
                    comment["influence"] = spans[0]["class"]
                    comment["age"] = spans[1].contents[0]
            #parse add datetime
            time_div = div.find("div", {"class":"zwlitime"})
            tmps = time_div.contents[0].split(" ")
            comment["add_datetime"] = "%s %s" % (tmps[1], tmps[3])
            #content
            content_div = div.find("div", {"class":"zwlitext stockcodec"})
            if content_div:
                content = u"%s" % content_div.contents
                content = content.replace("<br>", "\n").replace("</br>", "\n").strip("[]u'")
                comment["content"] = content
                
            
            self.result["comments"].append(comment)
            
        

class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "17299.txt"
        self.more_path = "full.txt"
        
    def test_parse(self):
        """http://guba.eastmoney.com/news,szzs,201434228.html
        """
        self.analysis = Analysis(self.path, "http://guba.eastmoney.com/news,szzs,201434228.html")
        self.analysis.parse()
        
        self.assertNotEqual(self.analysis.result, {})
        self.assertGreater(self.analysis.result["read_number"], 0)
        self.assertEqual(self.analysis.result["comment_number"], 0)
        self.assertIsNotNone(self.analysis.result["title"])
        self.assertIsNotNone(self.analysis.result["content"])
        
    def test_parse_more(self):
        """ http://guba.eastmoney.com/news,szzs,203294261.html
        """
        self.analysis = Analysis(self.more_path, "http://guba.eastmoney.com/news,szzs,203294261.html")
        self.analysis.parse()
        
        self.assertNotEqual(self.analysis.result, {})
        self.assertGreater(self.analysis.result["read_number"], 42424)
        self.assertEqual(self.analysis.result["comment_number"], 14)
        self.assertIsNotNone(self.analysis.result["title"])
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
    
    