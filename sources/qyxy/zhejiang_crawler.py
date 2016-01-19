#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import logging
import os
import sys
import time
import re
import settings
import json
import codecs
import unittest
from bs4 import BeautifulSoup
import CaptchaRecognition as CR

import random

urls = {
    'host': 'http://gsxt.zjaic.gov.cn/',
    'page_search': 'http://gsxt.zjaic.gov.cn/zhejiang.jsp',
    'page_Captcha': 'http://gsxt.zjaic.gov.cn/common/captcha/doReadKaptcha.do',
    'page_showinfo': 'http://gsxt.zjaic.gov.cn/search/doGetAppSearchResult.do',
    'prefix_url_0':'http://gsxt.zjaic.gov.cn/appbasicinfo/',
    'checkcode':'http://gsxt.zjaic.gov.cn//search/doValidatorVerifyCode.do',
}

headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36",
            #在获取验证码图片的时候，构造请求头的时候，要添加Referer
            "Referer" : "http://gsxt.zjaic.gov.cn/zhejiang.jsp",
        }

#HOSTS =["www.szcredit.com.cn", "121.8.226.101:7001", "gsxt.gdgs.gov.cn/aiccips"]

#http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=FC317A2A3B1A1A3B95FA8C3DE4DAFAED1E3E000779A9796D9F7A8DE8A59087BD
class ZhejiangCrawler(object):

    def __init__(self, json_restore_path):
        self.CR = CR.CaptchaRecognition("zhejiang")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_restore_path = json_restore_path
        self.html_restore_path = settings.html_restore_path + '/zhejiang/'
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/zhejiang/ckcode.jpg'
        self.path_captcha_diff = settings.json_restore_path +'/zhejiang/'

    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            settings.logger.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #settings.logger.debug("searchpage html :\n  %s", r.text)
        return r.text

    #获得搜索结果展示页面
    def get_page_showInfo(self, url, datas):
        r = self.requests.post( url, data = datas )
        if r.status_code != 200:
            return False
        r.encoding = "utf-8"
        #settings.logger.debug("showInfo page html :\n  %s", r.text)
        self.html_showInfo = r.text

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self):
        if self.html_showInfo is None:
            settings.logger.error(u"Getting Page ShowInfo failed\n")
        # call Object Analyze's method
        Ent = []
        soup = BeautifulSoup(self.html_showInfo, "html5lib")
        divs = soup.find_all("div", {"class":"list"})
        for div in divs:
            settings.logger.debug(u"div.ul.li.a['href'] = %s\n", div.ul.li.a['href'])
            Ent.append(div.ul.li.a['href'])
        self.ents = Ent

    # 破解验证码页面
    def crawl_page_captcha(self, url_search, url_Captcha, url_CheckCode,url_showInfo,  textfield= '330000000050426'):
        html_search = self.crawl_page_search(url_search)
        if not html_search:
            settings.logger.error(u"There is no search page")
        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha)
            if r.status_code != 200:
                settings.logger.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha, r.status_code)
                return
            if self.save_captcha(r.content):
                settings.logger.debug("Captcha is saved successfully \n" )
                result = self.crack_captcha()
                #print result
                datas= {
                        'name': textfield,
                        'verifyCode': result,
                }
                response = self.get_check_response(url_CheckCode, datas)
                # response返回的json结果: {u'flag': u'1', u'textfield': u'H+kiIP4DWBtMJPckUI3U3Q=='}
                if response['nameResponse'] == True:
                    datas_showInfo = {'textfield': response['textfield'], 'codeValue': result}
                    self.get_page_showInfo(url_showInfo, datas_showInfo)
                    break
                else:
                    settings.logger.debug(u"crack Captcha failed, the %d time(s)", count)
        return
    #获得验证的结果信息
    def get_check_response(self, url, datas):
        r = self.requests.post( url, data = datas )
        if r.status_code != 200:
            return False
        #print r.json()
        return r.json()
    #调用函数，破解验证码图片并返回结果
    def crack_captcha(self):
        if os.path.exists(self.path_captcha) is False:
            settings.logger.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]
        #print result
    # 保存验证码图片
    def save_captcha(self, Captcha):
        # 保存300张图片
        #url_Captcha = ("%scaptcha%f.jpeg")%(self.path_captcha_diff, random.uniform(1, 300))
        url_Captcha = self.path_captcha
        if Captcha is None:
            settings.logger.error(u"Can not store Captcha: None\n")
            return False

        f = open(url_Captcha, 'w')
        try:
            f.write(Captcha)
        except IOError:
            settings.logger.debug("%s can not be written", url_Captcha)
        finally:
            f.close
        return True
    """
    The following functions are for main page
    """

    """ 1. iterate enterprises in ents
        2. for each ent: decide host so that choose functions by pattern
        3. for each pattern, iterate urls
        4. for each url, iterate item in tabs
    """
    def crawl_page_main(self ):
        sub_json_dict= {}
        if not self.ents:
            settings.logger.error(u"Get no search result\n")
        try:

            for ent in self.ents:
                #http://www.szcredit.com.cn/web/GSZJGSPT/ QyxyDetail.aspx?rid=acc04ef9ac0145ecb8c87dd5710c2f86
                #http://121.8.226.101:7001/search/ search!entityShow?entityVo.pripid=440100100012003051400230
                #http://gsxt.gdgs.gov.cn/aiccips /GSpublicity/GSpublicityList.html?service=entInfo_+8/Z3ukM3JcWEfZvXVt+QiLPiIqemiEqqq4l7n9oAh/FI+v6zW/DL40+AV4Hja1y-dA+Hj5oOjXjQTgAhKSP1lA==

                #HOSTS =["www.szcredit.com.cn", "121.8.226.101:7001", "gsxt.gdgs.gov.cn"]

                m = re.match('http', ent)
                if m is None:
                    ent = urls['host']+ ent[3:]
                settings.logger.debug(u"ent url:%s\n"% ent)
                for i, item in enumerate(HOSTS):
                    if ent.find(item) != -1:

                        #"www.szcredit.com.cn"
                        if i==0:
                            settings.logger.info(u"This enterprise is type 0")
                            zhejiang = zhejiang0()
                            sub_json_dict =  zhejiang.run(ent)
                        #"121.8.226.101:7001"
                        elif i==1:
                            settings.logger.info(u"This enterprise is type 1")
                            zhejiang = zhejiang1()
                            sub_json_dict =  zhejiang.run(ent)
                        # gsxt.gdgs.gov.cn/aiccips
                        elif i==2:
                            settings.logger.info(u"This enterprise is type 2")
                            zhejiang = zhejiang2()
                            sub_json_dict = zhejiang.run(ent)
                        break
                else:
                    settings.logger.error(u"There are no response hosts\n")
        except Exception as e:
            settings.logger.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict


    def crawl_page_by_url(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            settings.logger.error(u"Getting page by url:%s\n, return status %s\n"% (url, r.status_code))
            return False
        # 为了防止页面间接跳转，获取最终目标url
        return {'page' : r.text, 'url': r.url}

    def crawl_page_by_url_post(self, url, data, header={}):
        if header:
            r = self.requests.post(url, data, headers= header)
        else :
            r = self.requests.post(url, data)
        if r.status_code != 200:
            settings.logger.error(u"Getting page by url with post:%s\n, return status %s\n"% (url, r.status_code))
            return False
        return {'page': r.text, 'url': r.url}

    # main function
    def run(self, ent_num):
        #if settingss.save_html and :
        #    print self.html_restore_path
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        self.json_dict = {}

        self.crawl_page_search(urls['page_search'])
        self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        self.analyze_showInfo()
        data = self.crawl_page_main()
        self.json_dict[ent_num] = data
        json_dump_to_file(self.json_restore_path , self.json_dict)

    def work(self, ent_num):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        self.crawl_page_captcha(urls['page_search'], urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)


def html_to_file(path, html):
    write_type = 'w'
    if os.path.exists(path):
        write_type = 'a'
    with codecs.open(path, write_type, 'utf-8') as f:
        f.write(html)

def json_dump_to_file(path, json_dict):
    write_type = 'w'
    if os.path.exists(path):
        write_type = 'a'
    with codecs.open(path, write_type, 'utf-8') as f:
        f.write(json.dumps(json_dict, ensure_ascii=False)+'\n')

def read_ent_from_file(path):
    read_type = 'r'
    if not os.path.exists(path):
        settings.logger.error(u"There is no path : %s"% path )
    lines = []
    with codecs.open(path, read_type, 'utf-8') as f:
        lines = f.readlines()
    lines = [ line.split(',') for line in lines ]
    return lines



if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    zhejiang = ZhejiangCrawler('./enterprise_crawler/zhejiang.json')
    zhejiang.work('330000000050426')



#     ents = read_ent_from_file("./enterprise_list/zhejiang.txt")
#     if not os.path.exists("./enterprise_crawler"):
#         os.makedirs("./enterprise_crawler")
#     zhejiang = ZhejiangCrawler('./enterprise_crawler/zhejiang.json')
#     for ent_str in ents:
#         settings.logger.info(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
#         zhejiang.run(ent_num = ent_str[2])
#         settings.logger.info(u'###################   Enterprise with id  %s Finished!  ###################\n' % ent_str[2])

