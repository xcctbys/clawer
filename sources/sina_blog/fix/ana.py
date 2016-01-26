#encoding=utf-8
"""sina blog analysis
http://blog.sina.com.cn/s/blog_4d89b8340102w2ej.html

hits: http://comet.blog.sina.com.cn/api?maintype=hits&act=4&aid=4d89b8340102w2ej&ref=&varname=requestId_31617693


"""

import json
import sys
import logging
import unittest
import requests
import os
import codecs

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
        #     self.text = r.text
        # else:
        with open(self.path, "r") as f:
            self.text = f.read()
        # print  self.text
        self.soup = BeautifulSoup(self.text, "html5lib")
        # print self.soup
        self.parse_uid()
        self.parse_title()
        self.parse_content()
        self.parse_tags()
        self.parse_add_datetime()
        self.parse_comment_number()
        self.parse_read_number()
        self.parse_favorite_number()
        self.parse_forward_number()
        logging.debug("result is %s", json.dumps(self.result, indent=4))
        
    def parse_uid(self):

        span = self.soup.find("span", {"class":"last"})
        if span:
            logging.debug("span is %s", span)
            a = span.find("a")
            tmps = a["href"].split("_")
            self.result["uid"] = int(filter(str.isdigit, tmps[1].encode("utf-8")))
        span2 = self.soup.find("h1", {"class": "headTitle headTit"})
        if span2:

            logging.debug("span2 is %s", span2)
            a = span2.find("a")
            tmps = a["href"].split("u/")
            self.result["uid"] = int(filter(str.isdigit, tmps[1].encode("utf-8")))

    def parse_title(self):

        h2 = self.soup.find("h2", {"class":"titName SG_txta"})
        if h2:
            title = h2.get_text()
            self.result["title"] = title.strip()
        h1 = self.soup.find("h1", {"class":"h1_tit"})
        if h1:
            title = h1.get_text()
            self.result["title"] = title.strip()
            
    def parse_content(self):
        div = self.soup.find("div", {"id":"sina_keyword_ad_area2"})
        self.result["content"] = div.get_text().strip()
    
    def parse_tags(self):
        self.result["tags"] = []

        td = self.soup.find("td", {"class":"blog_tag"})
        if td:

            h3s = td.find_all("h3")
            for h3 in h3s:
                self.result["tags"].append(h3.get_text().strip())

        td1 = self.soup.find("div", {"class": "tagbox"})
        if td1:
            h3s = td1.find_all("a")
            for h3 in h3s:
                self.result["tags"].append(h3.get_text().strip())

    def parse_add_datetime(self):
        span = self.soup.find("span", {"class":"time SG_txtc"})

        self.result["add_datetime"] = span.get_text().strip("()")

    def parse_comment_number(self):
        pass
    
    def parse_read_number(self):
        div = self.soup.find("div", {"class":"IL"})
        if div:
            spans = div.find_all("span")
            for span in spans:
                if "id" in span.attrs and span["id"].find("r_") == 0:
                    logging.debug("span %s", span)
                    if not span.get_text().strip("()"):
                        break
                    self.result["read_number"] = int(span.get_text().strip("()"))
                    break
        div1 = self.soup.find("div", {"class": "NE_txtA OL"})
        if div1:
            spans = div1.find_all("span")
            for span in spans:
                if "id" in span.attrs and span["id"].find("r_") == 0:
                    logging.debug("span %s", span)
                    if not span.get_text().strip("()"):
                        break
                    self.result["read_number"] = int(span.get_text().strip("()"))
                    break
    
    def parse_favorite_number(self):
        div = self.soup.find("div", {"class":"IL"})
        if div:
            spans = div.find_all("span")
            for span in spans:
                if "id" in span.attrs and span["id"].find("f_") == 0:
                    logging.debug("span %s", span)
                    if not span.get_text().strip("()"):
                        break
                    self.result["favorite_number"] = int(span.get_text().strip("()"))
                    break

        div1 = self.soup.find("div", {"class": "NE_txtA OL"})
        if div1:
            spans = div1.find_all("span")
            for span in spans:
                if "id" in span.attrs and span["id"].find("f_") == 0:
                    logging.debug("span %s", span)
                    if not span.get_text().strip("()"):
                        break
                    self.result["favorite_number"] = int(span.get_text().strip("()"))
                    break
    
    def parse_forward_number(self):
        div = self.soup.find("div", {"class":"IL"})
        if div:
            spans = div.find_all("span")
            for span in spans:
                if "id" in span.attrs and span["id"].find("z_") == 0:
                    logging.debug("span %s", span)
                    if not span.get_text().strip("()"):
                        break
                    self.result["forward_number"] = int(span.get_text().strip("()"))
                    break
        div1 = self.soup.find("div", {"class": "NE_txtA OL"})
        if div1:
            spans = div1.find_all("span")
            for span in spans:
                if "id" in span.attrs and span["id"].find("z_") == 0:
                    logging.debug("span %s", span)
                    if not span.get_text().strip("()"):
                        break
                    self.result["forward_number"] = int(span.get_text().strip("()"))
                    break


class TestAnalysis(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        # self.path = "595050.txt"
        
    def test_parse(self):
        """http://blog.sina.com.cn/s/blog_4d89b8340102w2ej.html
        """

        for filenname in os.listdir(r'./content/'):
            # pass
            # print os.getcwd()
            # print filenname
            if filenname == ".DS_Store":
                continue
            self.path = "%s%s" % ("content/", filenname)
            # print self.path
            self.analysis = Analysis(self.path, ",,,,")
            self.analysis.parse()

            self.assertNotEqual(self.analysis.result, {})
            # self.assertEqual(self.analysis.result["uid"], 1300871220)
            # self.assertIsNotNone(self.analysis.result["title"])
            # self.assertIsNotNone(self.analysis.result["content"])
            # self.assertGreater(len(self.analysis.result["tags"]), 0)
            # self.assertGreater(self.analysis.result["read_number"], 0)
            # self.assertIsNotNone(self.analysis.result["add_datetime"])

            # self.assertIsNotNone(self.analysis.result["add_datetime"])
            # self.assertIsNotNone(self.analysis.result["tags"])
            # self.assertIsNotNone(self.analysis.result["content"])
            # self.assertIsNotNone(self.analysis.result["title"])
            # self.assertIsNotNone(self.analysis.result["uid"])
            # self.assertIsNotNone(self.analysis.result["read_number"])
            os.remove(self.path)
            n = filenname.split("_")[1]
            n = n.split(".")[0]
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
    