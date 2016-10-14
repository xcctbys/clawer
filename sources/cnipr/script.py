#!/usr/bin/python
# encoding:utf-8
import requests
from bs4 import BeautifulSoup
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Crawler(object):
    def __init__(self,ent_name = "北京百度网讯科技有限公司"):
        self.reqst = requests.Session()
        self.reqst.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:49.0) Gecko/20100101 Firefox/49.0",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        self.ent_name = ent_name
        self.result_list = []

    def do_post(self, startnum="1"):
        # 'strWhere': "北京百度网讯科技有限公司",
        data = {
            'start': startnum,
            # 'limit': "10",
            'limit': "10",
            'strWhere': self.ent_name,
            'yuyijs': "",
            'saveFlag': "1",
            'keyword2Save': "",
            'key2Save': "",
            'dbScope': "1"
        }

        self.resp = self.reqst.post('http://search.cnipr.com/search!doOverviewSearch4Index.action', data=data)
        print self.resp
        print self.resp.content
        print '##########',self.resp.status_code

    def get_iprnum(self):
        print self.resp.status_code
        soup = BeautifulSoup(self.resp.content, 'html.parser')
        uls = soup.find_all('ul', attrs={'class': 'av-collapse'})
        if uls:
            print len(uls)
            targets = uls[0].find_all('a', attrs={'attrval': 'FMZL'})
            if targets:
                print '#####iprnum'
                print targets[0].find('span').get_text().strip('()')

    def get_initPagination(self):

        # str = 'fafsf 2332rf initPagination(324)'
        # result = re.search('initPagination\(\d*\)', str)

        result = re.search('initPagination\(\d*\)', self.resp.content)
        print result.group(0)
        initPagination = result.group(0)

        pagecount = int(re.findall(r"\d+\.?\d*", initPagination)[0])
        print '#####pagecount',pagecount
        return pagecount


    def get_item(self):
        soup = BeautifulSoup(self.resp.content, 'html.parser')
        items = soup.find_all('div', attrs={'class': 'g_item'})
        print items
        return items

    def parse_item(self,items):
        for item in items:
            content_dict = {}

            print item.find('li',attrs={'class': 'g_li'}).get_text().strip()
            print item.find('li',attrs={'class': 'g_li'})['title']
            print item.find('li',attrs={'class': 'g_li1'}).get_text().strip()

            #cor1有效 cor2在审  cor3无效
            if item.find('li',attrs={'class': 'g_li2 cor1'}):
                print item.find('li',attrs={'class': 'g_li2 cor1'}).get_text().strip()
            elif item.find('li',attrs={'class': 'g_li2 cor2'}):
                print item.find('li',attrs={'class': 'g_li2 cor2'}).get_text().strip()
            elif item.find('li',attrs={'class': 'g_li2 cor3'}):
                print item.find('li',attrs={'class': 'g_li2 cor3'}).get_text().strip()
            self.result_list.append(self.parse_item_content(item,content_dict))
            print self.result_list


    def parse_item_content(self,item, content_dict):
            content_item_text = item.find('div',attrs={'class': 'g_cont'}).get_text().strip()
            print content_item_text
            content_item = item.find('div',attrs={'class': 'g_cont'})

            tds = content_item.find_all('td')
            print '############'
            print tds
            key_list = [u"申请号：",
                        u"申请日：",
                        u"公开(公告)号：",
                        u"公开(公告)日：",
                        u"同日申请：",
                        u"分案原申请号：",
                        u"申请(专利权)人：",
                        u"分类号：",
                        u"优先权：",
                        u"摘要："]
            index = 0
            for td in tds:
                print '--------0'
                print td
                print '---------1'
                print td.get_text().strip()
                print '---------11'
                print type(td.get_text())
                print key_list[index]
                print td.get_text().replace(key_list[index],'',1).strip()
                print '--------2'
                content_dict[key_list[index]] = td.get_text().replace(key_list[index],'',1).strip()
                index +=1
            print content_dict
            return content_dict

    def run(self,startnum="1"):
        self.do_post(startnum)
        self.get_iprnum()
        # self.get_initPagination()
        its = cl.get_item()
        self.parse_item(its)


    def test(self):
            index = 0
            key_list = [u"申请号：",
                        u"申请日：",
                        u"公开(公告)号：",
                        u"公开(公告)日：",
                        u"同日申请：",
                        u"申请(专利权)人：",
                        u"分类号：",
                        u"优先权：",
                        u"摘要："]
            print key_list[1]
            print key_list[0]
            print key_list[index]



if __name__ == '__main__':
    cl = Crawler()
    cl.run()
    count = cl.get_initPagination()
    # for i in count-1:
    #     cl.run(str(i+1))

    for i in range(10):
        print i
        print type(i)
        cl.run(str(i+1))



