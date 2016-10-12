#!/usr/bin/python
# encoding:utf-8
import requests
from bs4 import BeautifulSoup

class Crawler(object):
    def __init__(self):
        self.reqst = requests.Session()
        self.reqst.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:49.0) Gecko/20100101 Firefox/49.0",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        self.ent_num = "北京百度网讯科技有限公司"
    def do_post(self):
        #'strWhere': "北京百度网讯科技有限公司",
        data = {
            'start': "1",
            'limit': "10",
            'strWhere': self.ent_num,
            'yuyijs': "",
            'saveFlag': "1",
            'keyword2Save': "",
            'key2Save': "",
            'dbScope': "1"
        }

        resp = self.reqst.post('http://search.cnipr.com/search!doOverviewSearch4Index.action', data=data)

    def
        print resp.status_code
        soup = BeautifulSoup(resp.content, 'html.parser')
        uls = soup.find_all('ul', attrs={'class': 'av-collapse'})
        if uls:
            print len(uls)
            targets = uls[0].find_all('a', attrs={'attrval': 'FMZL'})
            if targets:
                print targets[0].find('span').get_text().strip('()')
