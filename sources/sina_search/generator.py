# coding=utf-8
""" example is http://search.sina.com.cn/?c=news&q=%D0%DC%CA%D0+O%3A%C8%CB%C3%F1%C8%D5%B1%A8&range=all&num=10
"""

import re
import logging
import json
import urllib
import unittest
import requests

from bs4 import BeautifulSoup


DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


keywords = [
        u'股市',
        u'股票',
        u'股民',
        u'深证',
        u'上证',
        u'牛市',
        u'熊市',
        u'资本市场',
        u'金融市场',
        u'配资',
        u'A股',
        u'股指',
        u'期货',
        u'融资',
        u'融券',
        u'基金',
        u'证监会',
        u'新三板',
        u'创业板',
        u'银监会',
        u'保监会',
        u'央行'
]

medias = [
        u'人民日报',
        u'新华社'
]



class Generator(object):
    HOST = "http://search.sina.com.cn/?c=news&"

    def __init__(self):
        self.uris = set()

    def search_url(self, keywords, medias):
        for each in keywords:
            keyword = each
            for each in medias:
                media = each
                self.page_url(keyword, media)

    def page_url(self, keyword, media):
        url = self.HOST + urllib.urlencode({"q": keyword.encode("gbk")}) + '+O%3A'\
                   + urllib.quote(media.encode("gbk")) + '&range=all&num=20'
        self.obtain_urls(url)

    def obtain_urls(self, url):
        r = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)\
         AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        if r.status_code != 200:
            return

        soup = BeautifulSoup(r.text, "html5lib")
        num = str(soup.find('div', {'class', 'l_v2'}).contents).decode("unicode_escape").replace(',', '')
        news_count = int(re.findall(r'\d+', num)[0])
        self.do_obtain(news_count,url)

    def do_obtain(self, count, url):
        for i in range(1, ((count-1)/20)+2):
            page = url + '&col=&source=&from=&country=&size=&time=&a=&page=' + str(i) + \
                   '&pf=2131425492&ps=2132080888&dpc=1'
            r = requests.get(page, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)\
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
            if r.status_code != 200:
                return

            soup = BeautifulSoup(r.text, "html5lib")
            all_h = soup.find_all("h2")
            for h in all_h:
                news_a = h.find('a')
                news_link = news_a['href']
                if 'http://finance.sina.com' in news_link:
                    self.uris.add(news_link)



class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.search_url([u'熊市'], [u'人民日报', u'新华社'])

        for uri in self.generator.uris:
            logging.debug("urls is %s", uri)
        logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)



if __name__ == "__main__":

    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.search_url(keywords, medias)

    for uri in generator.uris:
        print json.dumps({"uri":uri})