#!/usr/bin/env python2
#encoding=utf-8
'''
crawler from http://gsxt.saic.gov.cn/, to get all the official website address of
all the provinces in China
'''

import sys
import json
import logging
import unittest
import requests
from bs4 import BeautifulSoup

g_debug = False
def InitLogging(DEBUG):
    if DEBUG:
        level = logging.DEBUG
    else:
        level = logging.ERROR
    logging.basicConfig(level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

class OrgUrlCrawler(object):
    def __init__(self, url = 'http://gsxt.saic.gov.cn/'):
        self.init_url = url
        self.header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'
        }

    def crawl(self):
        r = requests.get(self.init_url, self.header)
        if r.status_code != 200:
            logging.debug('crawler failed to crawl page %s' % self.init_url)
            return None
        return r.text

    def parse(self, page):
        #for jump out  multi-loop
        class FoundException(Exception):
            pass

        soup = BeautifulSoup(page)
        ul = None
        try:
            for ch in soup.body.children:
                if ch.name and ch['id'] == 'wrap':
                    for ch1 in ch.children:
                        if ch1.name and ch1['id'] == 'right':
                            for ch2 in ch1:
                                if ch2.name == 'ul':
                                    ul = ch2
                                    raise FoundException()
        except:
            print 'find ul element'
        finally:
            if ul: #got desired data, province and its url
                location_url_map = {}
                for ch in ul:
                    if ch.name == 'li':
                        for loc in ch:
                            if loc.name == 'a':
                                location_url_map[loc.string] = loc['href']

                with open('./init_urls.json', 'w') as f:
                    json.dump(location_url_map, f)
            else:
                return

    def work(self):
        page = self.crawl()
        if page:
            self.parse(page)


class Test_org_url_crawler(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.crawler = OrgUrlCrawler()
    '''
    def test_work(self):
        self.crawler.work()
    '''
    def test_parse(self):
        with open('./1.html', 'r') as f:
            self.crawler.parse(f)


if __name__ == '__main__':
    InitLogging(g_debug)
    if g_debug:
        unittest.main()

    crawler = OrgUrlCrawler()
    crawler.work()