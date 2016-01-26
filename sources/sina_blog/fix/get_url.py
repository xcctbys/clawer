# encoding=utf-8
""" example is http://blog.sina.com.cn/s/articlelist_1300871220_0_1.html
"""
import urllib
import json
import sys
import logging
import unittest
import requests
import os
import cPickle as pickle
import datetime

from bs4 import BeautifulSoup
import urlparse
try:
    import pwd
except:
    pass
import traceback


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

TOP_100_IDS = [
    1300871220,
    1216826604,
    1245296155,
    1284139322,
    1236135807,
    1285707277,
    1458594614,
    1504965870,
    1298535315,
    1279884602,
    1364334665,
    1278228085,
    1243037810,
    1319231304,
    1282871591,
    1243881594,
    1233227211,
    1279916282,
    1502087803,
    1638714710,
    1319802272,
    1305431810,
    1215172700,
    1249424622,
    1307309734,
    1617732512,
    1434387020,
    1278127565,
    1301484230,
    1649821184,
    1338707944,
    1603589321,
    1253205351,
    1092672395,
    1253386310,
    1258609013,
    1273642560,
    1483330984,
    1661526105,
    1500243557,
    1250075844,
    1290677635,
    1342877185,
    1791653972,
    1239417764,
    1092849864,
    1301047350,
    1319475951,
    1278226564,
    1349341797,
    1503072772,
    1264802107,
    1623430883,
    1220069571,
    1286519923,
    1366708375,
    1665967841,
    1244748717,
    1725765581,
    1349323031,
    1182389073,
    1507817532,
    1361584961,
    2892774000,
    1724710054,
    1418062403,
    1219262581,
    1199839991,
    1502620537,
    1251977337,
    1503491352,
    1272573150,
    2539920613,
    2744161330,
    1372231703,
    2160168205,
    1394379401,
    1217743083,
    1278084127,
    1747738261,
    1290699133,
    1302452922,
    1922761130,
    1408763403,
    1300112204,
    1225255825,
    1291592332,
    1190841165,
    1182426800,
    1274553861,
    1253039302,
    1160859960,
    1307994117,
    1343920131,
    1235833274,
    1252364410,
    1751100587,
    1147298365,
    1446362094,
    1259215934,
]




class History(object):


    def __init__(self):

        self.keyword_num = 0

        self.uid = TOP_100_IDS[0]
        self.count = 10


class Generator(object):
    HOST = "http://blog.sina.com.cn/"
    STEP = 1

    def __init__(self):
        self.uris = set()
        self.history = History()
        self.history_path = "tmp/sina_blog_byday"
        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))
        self.load_history()

    def load_history(self):

        if os.path.exists(self.history_path) is False:
            self.history = History()
            return

        with open(self.history_path, "r") as f:
            self.history = pickle.load(f)
            # self.history.keyword_num = self.history.history.keyword_num
            # self.history.last_time = self.history.this_time
            # self.history.keyword_num = 0
            # self.save_history()

    def save_history(self):
        with open(self.history_path, "w") as f:
            pickle.dump(self.history, f)
            if hasattr(self, "uid"):
                os.chown(self.history_path, self.uid, self.gid)

    def page_url(self, uid):
        return urlparse.urljoin(self.HOST, "/s/articlelist_%d_0_1.html" % uid)

    def obtain_urls(self):

        for position in range(self.history.keyword_num, self.history.keyword_num+100):

            if position >= len(TOP_100_IDS):
                position = len(TOP_100_IDS)-1

            self.history.uid = TOP_100_IDS[position]
            self.do_obtain(self.history.uid)

        # for position in range(self.history.keyword_num, self.history.keyword_num+5):
        #
        #     if position >= len(TOP_100_IDS):
        #         self.history.this_time = self.history.last_time + datetime.timedelta(self.STEP)
        #         self.history.count = self.history.count+10
        #         break
        #     self.history.uid = TOP_100_IDS[position]
        #     self.do_obtain(self.history.uid)
        # self.history.keyword_num += 99
        self.save_history()

    def do_obtain(self, uid):
        r = requests.get(self.page_url(uid), headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        # logging.debug(u"uid %s, page %s , text %s", uid, page, r.text)
        soup = BeautifulSoup(r.text, "html5lib")
        div = soup.find("div", {"class": "articleList"})
        try:
            spans = div.find_all("span", {"class": "atc_title"})
            for span in spans[50: 60]:
                self.uris.add(span.a["href"])
                logging.debug(u"url %s", span.a["href"])
        except:
            pass

    def download(self,url,n):

        # url= "http://paper.people.com.cn/rmrb/html/2015-01/24/nw.D110000renmrb_20150124_1-05.htm"
        # current_cookie = "username=bestjyz; expires=Thu, 12 Nov 2015 04:00:55 GMT; path=/; domain=paper.people.com.cn"
        r = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        if r.status_code != 200:
            return
        # path2 = ('e://plkj/peopledaily/%s.txt' % n
        path2 = "%s%s%s%s" % ('content/', n, "_1-9", ".txt")
        with open(path2, "w") as f:
            f.write(r.content)

class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()

        logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)
        self.assertGreater(self.generator.history.position, 0)

    def test_load_history(self):
        self.generator2 = Generator()
        self.generator2.load_history()
        logging.debug("current_day is %s", self.generator2.current_day)
        logging.debug("keyword_num is %s", self.generator2.keyword_num)


if __name__ == "__main__":
    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_urls()
    for uri in generator.uris:
        m = uri.split('_')[1]
        n = m.split(".")[0]
        generator.download(uri, n)
        print json.dumps({"uri": uri, "download_engine": "phantomjs"})