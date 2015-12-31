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
import urlparse
import codecs
import urllib
import urllib2
import cookielib

#import traceback
import unittest
from bs4 import BeautifulSoup
import CaptchaRecognition as CR
urls = {
    'host': 'http://gsxt.gdgs.gov.cn/aiccips/',
    'prefix_url':'http://www.szcredit.com.cn/web/GSZJGSPT/',
    'page_search': 'http://gsxt.gdgs.gov.cn/aiccips/index',
    'page_Captcha': 'http://gsxt.gdgs.gov.cn/aiccips/verify.html',
    'page_showinfo': 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html',
    'checkcode':'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/checkCode.html',
    'ind_comm_pub_reg_basic': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?',
    'ind_comm_pub_reg_shareholder': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!tzrFrame.dhtml?',
    'ind_comm_pub_reg_modify': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!biangengFrame.dhtml?',
    'ind_comm_pub_arch_key_persons': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!zyryFrame.dhtml?',
    'ind_comm_pub_arch_branch': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!fzjgFrame.dhtml?',
    'ind_comm_pub_arch_liquidation': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!qsxxFrame.dhtml?',
    'ind_comm_pub_movable_property_reg': 'http://qyxy.baic.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdyFrame.dhtml?',
    'ind_comm_pub_equity_ownership_reg': 'http://qyxy.baic.gov.cn/gdczdj/gdczdjAction!gdczdjFrame.dhtml?',
    'ind_comm_pub_administration_sanction': 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list.dhtml?',
    'ind_comm_pub_business_exception': 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_jyycxx.dhtml?',
    'ind_comm_pub_serious_violate_law':   'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_yzwfxx.dhtml?',
    'ind_comm_pub_spot_check':   'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_ccjcxx.dhtml?',
    'ent_pub_ent_annual_report':   'http://qyxy.baic.gov.cn/qynb/entinfoAction!qyxx.dhtml?',
    'ent_pub_shareholder_capital_contribution':   'http://qyxy.baic.gov.cn/gdcz/gdczAction!list_index.dhtml?',
    'ent_pub_equity_change':   'http://qyxy.baic.gov.cn/gdgq/gdgqAction!gdgqzrxxFrame.dhtml?',
    'ent_pub_administrative_license':   'http://qyxy.baic.gov.cn/xzxk/xzxkAction!list_index.dhtml?',
    'ent_pub_knowledge_property':   'http://qyxy.baic.gov.cn/zscqczdj/zscqczdjAction!list_index.dhtml?',
    'ent_pub_administration_sanction':   'http://qyxy.baic.gov.cn/gdgq/gdgqAction!qyxzcfFrame.dhtml?',
    'other_dept_pub_administrative_license':   'http://qyxy.baic.gov.cn/qtbm/qtbmAction!list_xzxk.dhtml?',
    'other_dept_pub_administrative_sancrtion':   'http://qyxy.baic.gov.cn/qtbm/qtbmAction!list_xzcf.dhtml?',

    'shareholder_detail':'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml?'
}
#debug control parameter
DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

##

headers = { 'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"}
HOSTS =["www.szcredit.com.cn", "121.8.226.101:7001", "gsxt.gdgs.gov.cn/aiccips"]
class Crawler(object):
    def __init__(self, analysis):
        self.analysis = analysis
        self.html_search = None
        self.html_showInfo = None
        self.Captcha = None
        #self.opener = self.make_opener()
        self.path_captcha = './Captcha.png'
        self.CR = CR.CaptchaRecognition("guangdong")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.main_host = ""
        self.json_dict={}



    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            logging.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #logging.debug("searchpage html :\n  %s", r.text)
        self.html_search = r.text
    #
    def get_page_showInfo(self, url, datas):
        r = self.requests.post( url, data = datas )
        if r.status_code != 200:
            return False
        r.encoding = "utf-8"
        #logging.debug("showInfo page html :\n  %s", r.text)
        self.html_showInfo = r.text

    #
    def analyze_showInfo(self):
        if self.html_showInfo is None:
            logging.error(u"Getting Page ShowInfo failed\n")
        # call Object Analyze's method
        self.ents = self.analysis.analyze_showInfo(self.html_showInfo)

            #
    def get_Ent(self, url_ent):
        r = self.requests.get( url_ent)
        if r.status_code != 200:
            return False
        r.encoding = "utf-8"


    #
    def crawl_page_captcha(self, url_Captcha, url_CheckCode,url_showInfo,  textfield= '440301102739085'):

        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha)
            if r.status_code != 200:
                logging.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha, r.status_code)
                return
            #print type(r.content), type(r.text)
            self.Captcha = r.content
            #logging.debug("Captcha page html :\n  %s", self.Captcha)
            if self.save_captcha():
                #logging.debug("Captcha is saved successfully \n" )
                result = self.crack_captcha()
                print result
                # post to checkCode.html
                datas= {
                        'textfield': textfield,
                        'code': result,
                }
                response = self.get_check_response(url_CheckCode, datas)
                # {u'flag': u'1', u'textfield': u'H+kiIP4DWBtMJPckUI3U3Q=='}
                if response['flag'] == '1':
                    datas_showInfo = {'textfield': response['textfield'], 'code': result}
                    self.get_page_showInfo(url_showInfo, datas_showInfo)
                    break
                else:
                    logging.debug(u"crack Captcha failed, the %d time(s)", count)
        #

        return
    #
    def get_check_response(self, url, datas):
        r = self.requests.post( url, data = datas )
        if r.status_code != 200:
            return False
        #print r.json()
        return r.json()
    #
    def crack_captcha(self):
        if os.path.exists(self.path_captcha) is False:
            logging.error(u"Captcha path is not found\n")
            return
        return self.CR.predict_result(self.path_captcha)
        #print result


    #
    def save_captcha(self):
        url_Captcha = self.path_captcha
        if self.Captcha is None:
            logging.error(u"Can not store Captcha: None\n")
            logging.debug(u"Can not store Captcha: None\n")
            return False

        f = open(url_Captcha, 'w')
        try:
            f.write(self.Captcha)
        except IOError:
            logging.debug("%s can not be written", url_Captcha)
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
            logging.error(u"Get no search result\n")
        try:

            for ent in self.ents:
                #http://www.szcredit.com.cn/web/GSZJGSPT/ QyxyDetail.aspx?rid=acc04ef9ac0145ecb8c87dd5710c2f86
                #http://121.8.226.101:7001/search/ search!entityShow?entityVo.pripid=440100100012003051400230
                #http://gsxt.gdgs.gov.cn/aiccips /GSpublicity/GSpublicityList.html?service=entInfo_+8/Z3ukM3JcWEfZvXVt+QiLPiIqemiEqqq4l7n9oAh/FI+v6zW/DL40+AV4Hja1y-dA+Hj5oOjXjQTgAhKSP1lA==

                #HOSTS =["www.szcredit.com.cn", "121.8.226.101:7001", "gsxt.gdgs.gov.cn"]
                logging.debug(u"ent name:%s\n"% ent)
                for i, item in enumerate(HOSTS):
                    if ent.find(item):
                        #crawl_page_main_by_pattern(item)
                        #"www.szcredit.com.cn"
                        if i==0:
                            #get rid
                            rid = ent[ent.index("rid")+4: len(ent)]
                            #logging.debug(u"Ent rid = %s\n", rid)
                            url = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=" + rid
                            sub_json_dict["crawl_ind_comm_pub_pages"] =  self.crawl_ind_comm_pub_pages(url, i)
                            url = "http://www.szcredit.com.cn/web/GSZJGSPT/QynbDetail.aspx?rid=" + rid
                            sub_json_dict["crawl_ent_pub_pages"] =  self.crawl_ent_pub_pages(url, i)
                            url = "http://www.szcredit.com.cn/web/GSZJGSPT/QtbmDetail.aspx?rid=" + rid
                            sub_json_dict["crawl_other_dept_pub_pages"] =  self.crawl_other_dept_pub_pages(url, i)
                            #json_dump_to_file("final_json.json", self.json_dict)

                        #"121.8.226.101:7001"
                        elif i==1:
                            pripid = ent[ent.index("pripid")+7: len(ent)]
                        # gsxt.gdgs.gov.cn/aiccips
                        elif i==2:
                            #http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo
                            #http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html
                            #http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html
                            #http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html
                            url = ent
                            sub_json_dict["crawl_ind_comm_pub_pages"] =  self.crawl_ind_comm_pub_pages(url, i)
                            url = "http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html"
                            sub_json_dict["crawl_ent_pub_pages"] =  self.crawl_ent_pub_pages(url, i)
                            url = "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html"
                            sub_json_dict["crawl_other_dept_pub_pages"] =  self.crawl_other_dept_pub_pages(url, i)
                            url = "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html"
                            sub_json_dict["crawl_judical_assist_pub_pages"] = self.crawl_judical_assist_pub_pages(url, i)


                            pass
                        else:
                            pass

                        break
                else:
                    logging.error(u"There are no response hosts\n")
        except Exception as e:
            logging.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #

    def crawl_xingzhengchufa_page(self, url, text):
        data = self.analysis.analyze_xingzhengchufa(text)
        r = self.requests.post( url, data)
        if r.status_code != 200:
            return False
        #html_to_file("xingzhengchufa.html",r.text)
        return r.text
    def crawl_biangengxinxi_page(self, url, text):
        datas = self.analysis.analyze_biangengxinxi(text)
        r2 = self.requests.post( url, datas, headers = {'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',})
        if r2.status_code != 200:
            return False
        #html_to_file("biangengxinxi.html",r2.text)
        return r2.text
    # 爬取 工商公示信息 页面
    def crawl_ind_comm_pub_pages(self, url, types):
        sub_json_dict={}
        try:
            if types == 0:
                page = self.crawl_page_by_url(url)['page']
                #html_to_file("pub.html", page)
                page_xingzhengchufa = self.crawl_xingzhengchufa_page(url, page)
                page_biangengxinxi = self.crawl_biangengxinxi_page(url, page_xingzhengchufa)
                for item in  (  'jibenxinxi',
                                'biangengxinxi',
                                'beian',
                                'dongchandiya',
                                'guquanchuzi',
                                'xingzhengchufa',
                                'jingyingyichang',
                                'yanzhongweifa',
                                'chouchajiancha',
                            ):
                    if item == 'biangengxinxi':
                        sub_json_dict[item] = self.analysis.parse_page(page_biangengxinxi, item)
                    elif item == 'xingzhengchufa':
                        sub_json_dict[item] = self.analysis.parse_page(page_xingzhengchufa, item)
                    else :
                        sub_json_dict[item] = self.analysis.parse_page(page, item)
            elif types==1:
                pass
            elif types == 2:
                page_entInfo = self.crawl_page_by_url(url)['page']
                data = self.analysis.parse_page_data_2(page_entInfo)

                #html_to_file("pub_page_2.html", page)
                tabs = [ 'entInfo',          # 登记信息
                        'entCheckInfo',     #备案信息
                        'pleInfo',          #动产抵押登记信息
                        'curStoPleInfo',    #股权出质
                        'cipPenaltyInfo',   #行政处罚
                        'cipUnuDirInfo',    #经营异常
                        'cipBlackInfo',     #严重违法
                        'cipSpotCheInfo',   #抽查检查
                        ]
                div_names = [    'jibenxinxi',
                                'beian',
                                'dongchandiya',
                                'guquanchuzi',
                                'xingzhengchufa',
                                'jingyingyichang',
                                'yanzhongweifa',
                                'chouchajiancha',
                            ]
                for tab, div_name in zip(tabs, div_names):
                    url = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service="+ tab
                    page = self.crawl_page_by_url_post(url, data)
                    sub_json_dict[div_name] =  self.analysis.parse_page_2(page, div_name)



        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s, type is %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict
        #json_dump_to_file("json_dict.json", self.json_dict)


    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url):
        sub_json_dict = {}
        try:
            page = self.crawl_page_by_url(url)['page']
            for item in (
                        'qiyenianbao', #企业投资人出资比例
                        'xingzhengxuke', #股权变更信息
                        'xingzhengchufa',#行政处罚
                        'zhishichanquan', #知识产权出质登记信息
                        'touziren', # 股东及出资信息
                        'gudongguquan'# 股权变更信息
                        ):
                sub_json_dict[item] = self.analysis.parse_page(page, item)
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ent_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
        #json_dump_to_file("json_dict.json", self.json_dict)

    #爬取 其他部门公示信息 页面
    def crawl_other_dept_pub_pages(self, url):
        sub_json_dict={}
        try:
            page = self.crawl_page_by_url(url)['page']
            for item in (   'xingzhengxuke',#行政许可信息
                            'xingzhengchufa'#行政处罚信息
                        ):
                sub_json_dict[item] = self.analysis.parse_page(page, item)
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
        #json_dump_to_file("json_dict.json", self.json_dict)

    #judical assist pub informations
    def crawl_judical_assist_pub_pages(self):
        pass

    def crawl_page_by_url(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            logging.error(u"Getting page by url:%s\n, return status %s\n"% (url, r.status_code))
            return False
        # 为了防止页面间接跳转，获取最终目标url
        return {'page' : r.text, 'url': r.url}

    def crawl_page_by_url_post(self, url, data):
        r = self.requests.post(url, data)
        if r.status_code != 200:
            logging.error(u"Getting page by url with post:%s\n, return status %s\n"% (url, r.status_code))
            return False
        return {'page': r.text, 'url': r.url}

    # main function
    def work(self):
        """
        ens = read_ent_from_file("./enterprise_list/guangdong.txt")
        #os.makedirs("./Guangdong")
        for i, ent in enumerate(ens):
            self.crawl_page_search(urls['page_search'])
            self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent[2])
            self.analyze_showInfo()
            data = self.crawl_page_main()
            self.json_dict[ent[0]] = data
            json_dump_to_file("./guangdong/final_json_%s.json" % ent[0], self.json_dict)
            logging.debug(u"Now %s was finished\n"% ent[0])
        """
        url = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_+8/Z3ukM3JcWEfZvXVt+QiLPiIqemiEqqq4l7n9oAh/FI+v6zW/DL40+AV4Hja1y-dA+Hj5oOjXjQTgAhKSP1lA=="
        self.crawl_ind_comm_pub_pages(url, 2)


class Analyze(object):

    crawler = None
    def __init__(self):
        self.Ent = []
        self.json_dict = {}


    # return the list of enterprises
    def analyze_showInfo(self, text):
        soup = BeautifulSoup(text, "html5lib")
        divs = soup.find_all("div", {"class":"list"})
        for div in divs:
            logging.debug(u"div.ul.li.a['href'] = %s\n", div.ul.li.a['href'])
            self.Ent.append(div.ul.li.a['href'])
        return self.Ent
    def analyze_xingzhengchufa(self, text):
        soup = BeautifulSoup(text, "html5lib")
        generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value']
        state = soup.find("input", {"id": "__VIEWSTATE"})['value']

        data = {
                '__VIEWSTATEGENERATOR':generator,
                '__VIEWSTATE': state,
                '__EVENTTARGET':'Timer1',
                'ScriptManager1':"xingzhengchufa|Timer1",
                '__EVENTARGUMENT':'',
                '__ASYNCPOST':'true',
        }
        return data
    def analyze_biangengxinxi(self, text):
        #soup = BeautifulSoup(text, "html5lib")
        pattern = re.compile(r'__VIEWSTATE\|(.*?)\|')
        viewstate_object = pattern.search(text)
        state = ""
        generator = ""
        if viewstate_object :
            state = viewstate_object.group().split('|')[1]
        else:
            print 'None'
        pattern = re.compile(r'__VIEWSTATEGENERATOR\|(.*?)\|')
        viewgenerator_object = pattern.search(text)
        if viewgenerator_object:
            generator = viewgenerator_object.group().split('|')[1]
        else:
            print "None"

        data = {
                '__VIEWSTATEGENERATOR':generator,
                '__VIEWSTATE': state,
                '__EVENTTARGET':'Timer2',
                'ScriptManager1':"biangengxinxi|Timer2",
                '__EVENTARGUMENT':'',
                '__ASYNCPOST':'true',
        }
        return data
    #
    def analyze_biangengxinxi_page(self, text):
        soup = BeautifulSoup(text, "html5lib")
        biangengxinxi_div = soup.find("table")
        trs = biangengxinxi_div.find_all("tr", {"width" : "95%"})
        biangengxinxi_name = ""
        titles = []
        results = []
        #print(biangengxinxi_div.prettify())
        for line, tr in enumerate(trs):
            if line==0:
                biangengxinxi_name =  tr.get_text().strip()
            elif line == 1:
                ths = tr.find_all("th")
                titles = [ th.get_text().strip() for th in ths]
            else:
                tds_tag = tr.find_all("td")
                tds = [td.get_text().strip() for td in tds_tag]
                results.append(dict(zip(titles, tds)))
        self.json_dict[biangengxinxi_name] = results
        json_dump_to_file("json_dict.json", self.json_dict)



    def get_raw_text_by_tag(self, tag):
        return tag.get_text().strip()

    def get_table_title(self, table_tag):
        if table_tag.find('tr'):
            if table_tag.find('tr').find('th'):
                return self.get_raw_text_by_tag(table_tag.find('tr').th)
            elif table_tag.find('tr').find('td'):
                return self.get_raw_text_by_tag(table_tag.find('tr').td)
        return ''

    def sub_column_count(self, th_tag):
        if th_tag.has_attr('colspan') and th_tag.get('colspan') > 1:
            return int(th_tag.get('colspan'))
        return 0

    def get_sub_columns(self, tr_tag, index, count):
        columns = []
        for i in range(index, index + count):
            th = tr_tag.find_all('th')[i]
            if not self.sub_column_count(th):
                columns.append(( self.get_raw_text_by_tag(th), self.get_raw_text_by_tag(th)))
            else:
            #if has sub-sub columns
                columns.append((self.get_raw_text_by_tag(th), self.get_sub_columns(tr_tag.nextSibling.nextSibling, 0, self.sub_column_count(th))))
        return columns

    #get column data recursively, use recursive because there may be table in table
    def get_column_data(self, columns, td_tag):
        if type(columns) == list:
            data = {}
            multi_col_tag = td_tag
            if td_tag.find('table'):
                multi_col_tag = td_tag.find('table').find('tr')
            if not multi_col_tag:
                logging.error('invalid multi_col_tag, multi_col_tag = %s', multi_col_tag)
                return data

            if len(columns) != len(multi_col_tag.find_all('td', recursive=False)):
                logging.error('column head size != column data size, columns head = %s, columns data = %s' % (columns, multi_col_tag.contents))
                return data

            for id, col in enumerate(columns):
                data[col[0]] = self.get_column_data(col[1], multi_col_tag.find_all('td', recursive=False)[id])
            return data
        else:
            return self.get_raw_text_by_tag(td_tag)

    def get_detail_link(self, bs4_tag):
        pattern = re.compile(r'http')
        if pattern.search(bs4_tag['href']):
            return bs4_tag['href']
        return urls['prefix_url'] + bs4_tag['href']

    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            tbody= bs_table.find_all('tbody')[1]
        else:
            tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')

        tr = None
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                tr = tbody.find('tr')
            else:
                tr = tbody.find_all('tr')[1]
                if not tr.find('th'):
                    tr = tbody.find_all('tr')[0]
                elif tr.find('td'):
                    tr = None
        else:
            if len(bs_table.find_all('tr')) <= 1:
                return None
            elif bs_table.find_all('tr')[0].find('th') and not bs_table.find_all('tr')[0].find('td') and len(bs_table.find_all('tr')[0].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[1].find('th') and not bs_table.find_all('tr')[1].find('td') and len(bs_table.find_all('tr')[1].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[1]
        #logging.debug(u"get_columns_of_record_table->tr:%s\n", tr)
        ret_val=  self.get_record_table_columns_by_tr(tr, table_name)
        #logging.debug(u"ret_val->%s\n", ret_val)
        return  ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th'))==0:
                logging.error(u"The table %s has no columns"% table_name)
                return columns
            for th in tr_tag.find_all('th'):
                #logging.debug(u"th in get_record_table_columns_by_tr =\n %s", th)
                col_name = self.get_raw_text_by_tag(th)
                if col_name and col_name not in columns:
                    if not self.sub_column_count(th):
                        columns.append((col_name, col_name))
                    else: #has sub_columns
                        columns.append((col_name, self.get_sub_columns(tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(th))))
                        sub_col_index += self.sub_column_count(th)
        except Exception as e:
            logging.error(u'exception occured in get_table_columns, except_type = %s, table_name = %s' % (type(e), table_name))
        finally:
            return columns


    # parse main page
    # return params are dicts
    def parse_page(self, page, types):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:

                    divs = soup.body.find('div', {"id": types})
                    table = None
                    if not divs:
                        table = soup.body.find('table')
                    else :
                        table = divs.find('table')
                    #print table
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            page_data[table_name] = self.parse_table(table, table_name, page)
                        table = table.nextSibling

                except Exception as e:
                    logging.error(u'parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_table(self, bs_table, table_name, page):
        table_dict = None
        try:
            # tb_title = self.get_table_title(bs_table)
            #this is a fucking dog case, we can't find tbody-tag in table-tag, but we can see tbody-tag in table-tag
            #in case of that, we use the whole html page to locate the tbody

            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            tbody = None
            if len(bs_table.find_all('tbody'))>1:
                tbody = bs_table.find_all('tbody')[1]
            else:
                tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')
            if columns:
                col_span = 0
                for col in columns:
                    if type(col[1]) == list:
                        col_span += len(col[1])
                    else:
                        col_span += 1

                column_size = len(columns)
                item_array = []
                if not tbody:
                    records_tag = bs_table
                else:
                    records_tag = tbody
                for tr in records_tag.find_all('tr'):
                    if tr.find('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'))
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)
                                    #html_to_file("next.html", detail_page['page'])
                                    if table_name == u'企业年报':
                                        #logging.debug(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')

                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page['page'], table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                else:
                                    #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            else:
                                item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            col_count += 1
                            if col_count == column_size:
                                item_array.append(item.copy())
                                col_count = 0
                    #this case is for the ind-comm-pub-reg-shareholders----details'table
                    #a fucking dog case!!!!!!
                    elif tr.find('td') and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
                        col_count = 0
                        sub_col_index = 0
                        item = {}
                        sub_item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'), page)
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                    html_to_file("next.html", detail_page['page'])

                                    if table_name == u'企业年报':
                                        #logging.debug(u"2next_url = %s, table_name= %s\n", next_url, table_name)

                                        page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page['page'], table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                else:
                                    #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            else:
                                if type(columns[col_count][1]) == list:
                                    sub_key = columns[col_count][1][sub_col_index][1]
                                    sub_item[sub_key] = self.get_raw_text_by_tag(td)
                                    sub_col_index += 1
                                    if sub_col_index == len(columns[col_count][1]):
                                        item[columns[col_count][0]] = sub_item.copy()
                                        sub_item = {}
                                        col_count += 1
                                        sub_col_index = 0
                                else:
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                    col_count += 1
                            if col_count == column_size:
                                item_array.append(item.copy())
                                col_count = 0

                table_dict = item_array
            else:
                table_dict = {}
                for tr in bs_table.find_all('tr'):
                    if tr.find('th') and tr.find('td'):
                        ths = tr.find_all('th')
                        tds = tr.find_all('td')
                        if len(ths) != len(tds):
                            logging.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
        except Exception as e:
            logging.error(u'parse table %s failed with exception %s' % (table_name, type(e)))
            raise e
        finally:
            return table_dict

    def parse_report_table(self, table, table_name):
        table_dict = {}

        try:
            if table_name == u'基本信息':
                rowspan_name = ""
                item={}
                sub_item= {}
                trs = table.find_all("tr")[1:]
                i =0
                while i < len(trs):
                    tr  = trs[i]
                    titles = tr.find_all("td", {"align": True})
                    datas = tr.find_all("td", {"align": False})
                    if len(titles) != len(datas):
                        if len(titles) - len(datas) == 1:
                            row_num = int(titles[0]['rowspan'])
                            rowspan_name = titles[0].get_text().strip()
                            sub_item = {}
                            sub_item.update(dict(zip([ t.get_text().strip() for t in titles[1:]], [d.get_text().strip() for d in datas])))
                            j=1
                            while j < row_num:
                                tr= trs[i + j]
                                titles = tr.find_all("td", {"align": True})
                                datas = tr.find_all("td", {"align": False})
                                sub_item.update(dict(zip([t.get_text().strip() for t in titles], [ d.get_text().strip() for d in datas])))
                                j= j+1
                            i = i+ row_num-1
                            item[rowspan_name] = sub_item
                            #json_dump_to_file("sub_item.json", item)

                    else:
                        item.update(dict(zip([t.get_text().strip() for t in titles], [ d.get_text().strip() for d in datas])))
                    i+=1
                #json_dump_to_file("sub_item.json", item)

                table_dict[table_name] = item
            else:
                item={}
                sub_item= []
                tables = table.find_all("tr")[1:]

                while tables:
                    tds =  tables[0].find_all("td")
                    flag = False
                    for td in tds:
                        if not td.has_attr('align'):
                            flag = True
                            break
                    #如果第一排有横向的数据
                    if flag:
                        first_line = tables[0].find_all("td")
                        item[first_line[0].get_text().strip()] = first_line[1].get_text().strip()
                        tables = tables[1:]
                        continue
                    columns = [ td.get_text().strip() for td in tables[0].find_all("td")]
                    for tr in tables[1:]:
                        data = [td.get_text().strip() for td in tr.find_all("td")]
                        sub_item.append( dict( zip(columns, data)) )
                    item['list'] = sub_item
                    break

                table_dict[table_name] = item

        except Exception as e:
            logging.error(u"parse report table %s failed with exception %s\n"%(table_name, type(e)))
            raise e

        return table_dict

    def parse_ent_pub_annual_report_page(self, page_dict, table_name):
        url = page_dict['url']
        page = page_dict['page']
        page_data= {}
        soup = BeautifulSoup(page, "html5lib")
        number = len(soup.find('ul', {'id': 'ContentPlaceHolder1_ulTag'}).find_all('li'))
        if number == 0 :
            logging.error(u"Could not find tab in annual report page")
            return
        generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value']
        validation = soup.find("input", {"id": "__EVENTVALIDATION"})['value']
        state = soup.find("input", {"id": "__VIEWSTATE"})['value']
        ContentPlaceHolder = "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$lbtnTag0"
        target = "ctl00$ContentPlaceHolder1$lbtnTag0"
        data= {
            'ctl00$ContentPlaceHolder1$smObj':ContentPlaceHolder, #ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$lbtnTag1
            '__EVENTTARGET': target,   #ctl00$ContentPlaceHolder1$lbtnTag0
            '__EVENTARGUMENT': '',
            '__VIEWSTATE':state,
            '__VIEWSTATEGENERATOR':generator,
            '__EVENTVALIDATION':validation,
            '__ASYNCPOST':'true',
        }
        r = self.crawler.requests.post(url, data, headers = {'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'} )
        if r.status_code != 200:
            logging.error(u'Could not get response page')
            return False
        page = r.text
        #html_to_file("annual.html", page)
        table_name = ""
        try:
            soup = BeautifulSoup(page, 'html5lib')
            content_table = soup.find_all('table')[1:]
            for table in content_table:
                table_name = self.get_table_title(table)
                #logging.debug(u"annual report table_name= %s\n", table_name)
                table_data = self.parse_report_table(table, table_name)
                page_data[table_name] = table_data
        except Exception as e:
            logging.error(u'annual page: fail to get table data with exception %s' % e)
            raise e

        #html_to_file("annual.html", page)
        for i in range(number-1):
            state = re.compile(r"__VIEWSTATE\|(.*?)\|").search(page).group().split('|')[1]
            generator = re.compile(r"__VIEWSTATEGENERATOR\|(.*?)\|").search(page).group().split('|')[1]
            validation = re.compile(r"__EVENTVALIDATION\|(.*?)\|").search(page).group().split('|')[1]
            ContentPlaceHolder = "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$lbtnTag%d"%(i+1)
            target = "ctl00$ContentPlaceHolder1$lbtnTag%d"%(i+1)
            data= {
                'ctl00$ContentPlaceHolder1$smObj':ContentPlaceHolder, #ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$lbtnTag1
                '__EVENTTARGET': target,   #ctl00$ContentPlaceHolder1$lbtnTag0
                '__EVENTARGUMENT': '',
                '__VIEWSTATE':state,
                '__VIEWSTATEGENERATOR':generator,
                '__EVENTVALIDATION':validation,
                '__ASYNCPOST':'true',
            }
            r = self.crawler.requests.post(url, data, headers = {'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',} )
            if r.status_code != 200:
                logging.error(u'Could not get response page')
                return False
            page = r.text
            #html_to_file("annual.html", page)
            table_name = ""
            try:
                soup = BeautifulSoup(page, 'html5lib')
                content_table = soup.find_all('table')[1:]
                for table in content_table:
                    table_name = self.get_table_title(table)
                    #logging.debug(u"annual report table_name= %s\n", table_name)
                    table_data = self.parse_report_table(table, table_name)
                    #json_dump_to_file('report_json.json', table_data)
                    page_data[table_name] = table_data

            except Exception as e:
                logging.error(u'annual page: fail to parse page with exception %s'%e)
                raise e
        #json_dump_to_file('report_json.json', page_data)
        return page_data
    # 如果是第二种： http://gsxt.gdgs.gov.cn/aiccips/ q情况
    def parse_page_data_2(self, page):
        """
        <input type="hidden" id="aiccipsUrl" value="http://gsxt.gdgs.gov.cn/aiccips/">
        <input type="hidden" id="entNo" name="entNo" value="031ccfe1-54f9-449a-9c7f-ceaff0142fa1">
        <input type="hidden" id="entType" name="entType" value="1200  ">
        <input type="hidden" id="regOrg" name="regOrg" value="441300">
        """
        data= {
            "aiccipsUrl": "",
            "entNo": "",
            "entType":"",
            "regOrg":"",
        }
        try:
            soup = BeautifulSoup(page, "html5lib")
            data['aiccipsUrl'] = soup.find("input", {"id": "aiccipsUrl"})['value']
            data['entNo'] = soup.find("input", {"id": "entNo"})['value']
            data['entType'] = soup.find("input", {"id": "entType"})['value']+"++"
            data['regOrg'] = soup.find("input", {"id": "regOrg"})['value']

        except Exception as e:
            logging.error(u"parse page failed in function parse_page_data_2\n" )
            raise e
        finally
            return data

    def parse_page_2(self, page, div_id):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:
                    divs = soup.body.find('div', {"id": div_id})
                    table = None
                    if not divs:
                        table = soup.body.find('table')
                    else :
                        table = divs.find('table')
                    #print table
                    table_name = ""
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            page_data[table_name] = self.parse_table_2(table, columns)
                        elif table.name == 'div':
                            if not columns:
                                logging.error(u"Can not find columns when parsing page 2, table :%s"%div_id)
                                break
                            page_data[table_name] =  self.parse_table_2(table, columns)
                        table = table.nextSibling

                except Exception as e:
                    logging.error(u'parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_table_2(self, bs_table, columns ):
        table_dict = None
        try:
            # tb_title = self.get_table_title(bs_table)
            #this is a fucking dog case, we can't find tbody-tag in table-tag, but we can see tbody-tag in table-tag
            #in case of that, we use the whole html page to locate the tbody

            if columns:
                col_span = 0
                for col in columns:
                    if type(col[1]) == list:
                        col_span += len(col[1])
                    else:
                        col_span += 1

                column_size = len(columns)
                item_array = []
                records_tag = bs_table
                for tr in records_tag.find_all('tr'):
                    if tr.find('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'))
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)
                                    #html_to_file("next.html", detail_page['page'])
                                    if table_name == u'企业年报':
                                        #logging.debug(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')

                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page['page'], table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                else:
                                    #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            else:
                                item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            col_count += 1
                            if col_count == column_size:
                                item_array.append(item.copy())
                                col_count = 0
                    #this case is for the ind-comm-pub-reg-shareholders----details'table
                    #a fucking dog case!!!!!!
                    elif tr.find('td') and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
                        col_count = 0
                        sub_col_index = 0
                        item = {}
                        sub_item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'), page)
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                    html_to_file("next.html", detail_page['page'])

                                    if table_name == u'企业年报':
                                        #logging.debug(u"2next_url = %s, table_name= %s\n", next_url, table_name)

                                        page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page['page'], table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                else:
                                    #item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                            else:
                                if type(columns[col_count][1]) == list:
                                    sub_key = columns[col_count][1][sub_col_index][1]
                                    sub_item[sub_key] = self.get_raw_text_by_tag(td)
                                    sub_col_index += 1
                                    if sub_col_index == len(columns[col_count][1]):
                                        item[columns[col_count][0]] = sub_item.copy()
                                        sub_item = {}
                                        col_count += 1
                                        sub_col_index = 0
                                else:
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                    col_count += 1
                            if col_count == column_size:
                                item_array.append(item.copy())
                                col_count = 0

                table_dict = item_array
            else:
                table_dict = {}
                for tr in bs_table.find_all('tr'):
                    if tr.find('th') and tr.find('td'):
                        ths = tr.find_all('th')
                        tds = tr.find_all('td')
                        if len(ths) != len(tds):
                            logging.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
        except Exception as e:
            logging.error(u'parse table %s failed with exception %s' % (table_name, type(e)))
            raise e
        finally:
            return table_dict
        pass


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
        logging.error(u"There is no path : %s"% path )
    lines = []
    with codecs.open(path, read_type, 'utf-8') as f:
        lines = f.readlines()
    lines = [ line.split(',') for line in lines ]
    return lines


class Guangdong(object):
    def __init__(self):
        self.analysis = Analyze()
        self.crawler = Crawler(self.analysis)
        self.analysis.crawler = self.crawler

    def run(self):
        self.crawler.work()


if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    guangdong = Guangdong()
    guangdong.run()

