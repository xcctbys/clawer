#encoding=utf-8
"""china court

hits: http://www.zhihu.com/question/20239155
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
            self.text = r.text
        else:
            with open(self.path, "r") as f:
                self.text = f.read()
        try:
            self.soup = BeautifulSoup(self.text, "html5lib")
        except:
            self.soup = BeautifulSoup(self.text, "html.parser")
        self.parse_title()
        self.parse_content()
        self.parse_tags()
        self.parse_answer_count()
        self.parse_answer()
        logging.debug("result is %s", json.dumps(self.result, indent=4))
        
    def parse_title(self):
        div = self.soup.find("div", {"id":"zh-question-title"})
        h2 = div.find("h2", {"class":"zm-item-title zm-editable-content"})
        title = h2.get_text().strip()
        self.result["title"] = title.strip()
            
    def parse_content(self):
        div = self.soup.find("div", {"id":"zh-question-detail"})
        self.result["content"] = div.get_text().strip()
        
    def parse_tags(self):
        div = self.soup.find("div", {"class":"zm-tag-editor-labels zg-clear"})
        all_a = div.find_all("a")
        self.result["tags"] = []
        for a in all_a:
            self.result["tags"].append(a.get_text().strip())
            
    def parse_answer_count(self):
        div = self.soup.find("div", {"class":"zh-answers-title clearfix"})
        if not div:
            return
        h3 = div.find("h3")
        if h3:
            self.result["answer_count"] = int(h3["data-num"])
            
    def parse_answer(self):
        self.result["answers"] = []
        
        divs = self.soup.find_all("div", {"class":"zm-item-answer  zm-item-expanded"})
        for div in divs:
            answer = {}
            #parse answer author
            author_info_div = div.find("div", {"class":"zm-item-answer-author-info"})
            author_link = author_info_div.find("a", {"class":"author-link"})
            if author_link:
                answer["author_name"] = author_link.get_text().strip()
                answer["author_url"] = author_link["href"]
            #vote
            vote_div = div.find("div", {"class":"zm-item-vote-info"})
            answer["vote_count"] = int(vote_div.attrs["data-votecount"])
            #print "vote count %d" % answer["vote_count"]
            #content
            content_div = div.find("div", {"class":"zm-editable-content clearfix"})
            answer["content"] = content_div.get_text().strip()
            self.result["answers"].append(answer)
    

class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.path = "595050.txt"
        
    def test_parse(self):
        """http://blog.sina.com.cn/s/blog_4d89b8340102w2ej.html
        """
        self.analysis = Analysis(self.path, "http://www.zhihu.com/question/20239155")
        self.analysis.parse()
        
        self.assertNotEqual(self.analysis.result, {})
        self.assertIsNotNone(self.analysis.result["title"])
        self.assertIsNotNone(self.analysis.result["content"])
        self.assertIsNotNone(self.analysis.result["tags"])
        self.assertIsNotNone(self.analysis.result["answer_count"])    
        
    def test_parse1(self):
        url = "http://www.zhihu.com/question/19566962"
        
        self.analysis = Analysis(self.path, url)
        self.analysis.parse()
        
        self.assertNotEqual(self.analysis.result, {})
        self.assertIsNotNone(self.analysis.result["title"])
        self.assertIsNotNone(self.analysis.result["content"])
        self.assertIsNotNone(self.analysis.result["tags"])
        self.assertIsNotNone(self.analysis.result["answer_count"])


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
    
    