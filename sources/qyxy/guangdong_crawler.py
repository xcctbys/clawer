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
from Guangdong0 import Guangdong0
from Guangdong1 import Guangdong1
from Guangdong2 import Guangdong2

urls = {
    'host': 'http://gsxt.gdgs.gov.cn/aiccips/',
    'prefix_url_0':'http://www.szcredit.com.cn/web/GSZJGSPT/',
    'prefix_url_1':'http://121.8.226.101:7001/search/',
    'page_search': 'http://gsxt.gdgs.gov.cn/aiccips/index',
    'page_Captcha': 'http://gsxt.gdgs.gov.cn/aiccips/verify.html',
    'page_showinfo': 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html',
    'checkcode':'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/checkCode.html',
    'ind_comm_pub_reg_basic': 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo',
    'prefix_GSpublicity':'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=',
    'ind_comm_pub_reg_shareholder': 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/invInfoPage.html',                 #股东信息表的翻页
    'ind_comm_pub_reg_modify': 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/entChaPage',                            #变更信息表的翻页
    'ind_comm_pub_arch_key_persons': 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/vipInfoPage',                     #主要人员表的翻页
    'ind_comm_pub_arch_branch': 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/braInfoPage',                          #分支机构信息表的翻页
    'shareholder_detail':'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml?'
}
#debug control parameter
DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
formatter = logging.Formatter("%(levelname)s %(asctime)s %(lineno)d:: %(message)s")
filename = 'guangdong/mylog.log'
#logging.basicConfig(level=level, format=formatter)
fh = logging.FileHandler(filename)
fh.setLevel(level)
fh.setFormatter(formatter)
ch = logging.StreamHandler()
ch.setLevel(level)
ch.setFormatter(formatter)

logger = logging.getLogger('guangdong')
logger.setLevel(level)

logger.addHandler(fh)
logger.addHandler(ch)



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
    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            logger.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #logger.debug("searchpage html :\n  %s", r.text)
        self.html_search = r.text
    #获得搜索结果展示页面
    def get_page_showInfo(self, url, datas):
        r = self.requests.post( url, data = datas )
        if r.status_code != 200:
            return False
        r.encoding = "utf-8"
        #logger.debug("showInfo page html :\n  %s", r.text)
        self.html_showInfo = r.text

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self):
        if self.html_showInfo is None:
            logger.error(u"Getting Page ShowInfo failed\n")
        # call Object Analyze's method
        self.ents = self.analysis.analyze_showInfo(self.html_showInfo)

    # 破解验证码页面
    def crawl_page_captcha(self, url_Captcha, url_CheckCode,url_showInfo,  textfield= '440301102739085'):

        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha)
            if r.status_code != 200:
                logger.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha, r.status_code)
                return
            self.Captcha = r.content
            #logger.debug("Captcha page html :\n  %s", self.Captcha)
            if self.save_captcha():
                logger.debug("Captcha is saved successfully \n" )
                result = self.crack_captcha()
                print result
                datas= {
                        'textfield': textfield,
                        'code': result,
                }
                response = self.get_check_response(url_CheckCode, datas)
                # response返回的json结果: {u'flag': u'1', u'textfield': u'H+kiIP4DWBtMJPckUI3U3Q=='}
                if response['flag'] == '1':
                    datas_showInfo = {'textfield': response['textfield'], 'code': result}
                    self.get_page_showInfo(url_showInfo, datas_showInfo)
                    break
                else:
                    logger.debug(u"crack Captcha failed, the %d time(s)", count)
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
            logger.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        print result
        return result[1]
        #print result
    # 保存验证码图片
    def save_captcha(self):
        url_Captcha = self.path_captcha
        if self.Captcha is None:
            logger.error(u"Can not store Captcha: None\n")
            logger.debug(u"Can not store Captcha: None\n")
            return False

        f = open(url_Captcha, 'w')
        try:
            f.write(self.Captcha)
        except IOError:
            logger.debug("%s can not be written", url_Captcha)
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
            logger.error(u"Get no search result\n")
        try:

            for ent in self.ents:
                #http://www.szcredit.com.cn/web/GSZJGSPT/ QyxyDetail.aspx?rid=acc04ef9ac0145ecb8c87dd5710c2f86
                #http://121.8.226.101:7001/search/ search!entityShow?entityVo.pripid=440100100012003051400230
                #http://gsxt.gdgs.gov.cn/aiccips /GSpublicity/GSpublicityList.html?service=entInfo_+8/Z3ukM3JcWEfZvXVt+QiLPiIqemiEqqq4l7n9oAh/FI+v6zW/DL40+AV4Hja1y-dA+Hj5oOjXjQTgAhKSP1lA==

                #HOSTS =["www.szcredit.com.cn", "121.8.226.101:7001", "gsxt.gdgs.gov.cn"]

                m = re.match('http', ent)
                if m is None:
                    ent = urls['host']+ ent[3:]
                logger.debug(u"ent name:%s\n"% ent)
                for i, item in enumerate(HOSTS):
                    if ent.find(item) != -1:

                        #"www.szcredit.com.cn"
                        if i==0:
                            Guangdong = Guangdong0()
                            sub_json_dict =  Guangdong.run(ent)
                            """
                            rid = ent[ent.index("rid")+4: len(ent)]
                            #logger.debug(u"Ent rid = %s\n", rid)
                            url = "http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?rid=" + rid
                            sub_json_dict.update(self.crawl_ind_comm_pub_pages(url, i))
                            url = "http://www.szcredit.com.cn/web/GSZJGSPT/QynbDetail.aspx?rid=" + rid
                            sub_json_dict.update(self.crawl_ent_pub_pages(url, i))
                            url = "http://www.szcredit.com.cn/web/GSZJGSPT/QtbmDetail.aspx?rid=" + rid
                            sub_json_dict.update(self.crawl_other_dept_pub_pages(url, i))
                            #json_dump_to_file("final_json.json", self.json_dict)
                            """
                        #"121.8.226.101:7001"
                        elif i==1:
                            print "1"
                            guangdong = Guangdong1()
                            sub_json_dict =  guangdong.run(ent)
                            """
                            pripid = ent[ent.index("pripid")+7: len(ent)]
                            url = "http://121.8.226.101:7001/search/search!entityShow?entityVo.pripid=" + pripid
                            sub_json_dict.update(self.crawl_ind_comm_pub_pages(url, i))
                            url = "http://121.8.226.101:7001/search/search!enterpriseShow?entityVo.pripid="+ pripid
                            sub_json_dict.update(self.crawl_ent_pub_pages(url, i))
                            url = "http://121.8.226.101:7001/search/search!otherDepartShow?entityVo.pripid=" + pripid
                            sub_json_dict.update(self.crawl_other_dept_pub_pages(url, i))
                            url = "http://121.8.226.101:7001/search/search!judicialShow?entityVo.pripid=" + pripid
                            sub_json_dict.update(self.crawl_judical_assist_pub_pages(url, i))
                            """
                        # gsxt.gdgs.gov.cn/aiccips
                        elif i==2:
                            print '2'
                            guangdong = Guangdong2()
                            sub_json_dict = guangdong.run(ent)
                            """
                            url = ent
                            page_entInfo = self.crawl_page_by_url(url)['page']
                            post_data = self.analysis.parse_page_data_2(page_entInfo)
                            sub_json_dict.update(self.crawl_ind_comm_pub_pages(url, i, post_data))
                            url = "http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html"
                            sub_json_dict.update(self.crawl_ent_pub_pages(url, i, post_data))
                            url = "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html"
                            sub_json_dict.update(self.crawl_other_dept_pub_pages(url, i, post_data))
                            url = "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html"
                            sub_json_dict.update(self.crawl_judical_assist_pub_pages(url, i, post_data))
                            """
                        break
                else:
                    logger.error(u"There are no response hosts\n")
        except Exception as e:
            logger.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    # 对于第一种类型的页面获取行政处罚表格
    def crawl_xingzhengchufa_table_0(self, url, text):
        data = self.analysis.analyze_xingzhengchufa(text)
        r = self.requests.post( url, data)
        if r.status_code != 200:
            return False
        #html_to_file("xingzhengchufa.html",r.text)
        return r.text
    #对于第一种类型的页面获取 变更信息表格
    def crawl_biangengxinxi_table_0(self, url, text):
        datas = self.analysis.analyze_biangengxinxi(text)
        r2 = self.requests.post( url, datas, headers = {'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',})
        if r2.status_code != 200:
            return False
        #html_to_file("biangengxinxi.html",r2.text)
        return r2.text
    # 爬取 工商公示信息 页面
    def crawl_ind_comm_pub_pages(self, url, types, post_data= {}):
        sub_json_dict={}
        try:
            if types == 0:
                page = self.crawl_page_by_url(url)['page']
                #html_to_file("pub.html", page)
                table_xingzhengchufa = self.crawl_xingzhengchufa_table_0(url, page)
                table_biangengxinxi = self.crawl_biangengxinxi_table_0(url, table_xingzhengchufa)
                """
                'ind_comm_pub_reg_basic',  #登记信息-基本信息
                'ind_comm_pub_reg_shareholder', # 登记信息-股东信息
                'ind_comm_pub_reg_modify', # 登记信息-变更信息
                'ind_comm_pub_arch_key_persons', # 备案信息-主要人员信息
                'ind_comm_pub_arch_branch', # 备案信息-分支机构信息
                'ind_comm_pub_arch_liquidation', # 备案信息-清算信息
                'ind_comm_pub_movable_property_reg', # 动产抵押登记信息
                'ind_comm_pub_equity_ownership_reg', # 股权出置登记信息
                'ind_comm_pub_administration_sanction', # 行政处罚信息
                'ind_comm_pub_business_exception', # 经营异常信息
                'ind_comm_pub_serious_violate_law', # 严重违法信息
                'ind_comm_pub_spot_check', # 抽查检查信息
                """
                sub_json_dict['ind_comm_pub_reg_basic'], sub_json_dict['ind_comm_pub_reg_shareholder'] = self.analysis.parse_page(page, 'jibenxinxi')
                a, sub_json_dict['ind_comm_pub_arch_key_persons'], sub_json_dict['ind_comm_pub_arch_branch'], sub_json_dict['ind_comm_pub_arch_liquidation'] = self.analysis.parse_page(page, 'beian')
                sub_json_dict['ind_comm_pub_reg_modify'] = self.analysis.parse_page(table_biangengxinxi, 'biangengxinxi')
                sub_json_dict['ind_comm_pub_movable_property_reg'] = self.analysis.parse_page(page, 'dongchandiya')
                sub_json_dict['ind_comm_pub_equity_ownership_reg'] = self.analysis.parse_page(page, 'guquanchuzi')
                sub_json_dict['ind_comm_pub_business_exception'] = self.analysis.parse_page(page, 'jingyingyichang')
                sub_json_dict['ind_comm_pub_serious_violate_law'] = self.analysis.parse_page(page, 'yanzhongweifa')
                sub_json_dict['ind_comm_pub_spot_check'] = self.analysis.parse_page(page, 'chouchajiancha')
                sub_json_dict['ind_comm_pub_administration_sanction'] = self.analysis.parse_page(table_biangengxinxi, 'xingzhengchufa')

            elif types==1:
                page = self.crawl_page_by_url(url)['page']
                sub_json_dict['ind_comm_pub_reg_basic'], sub_json_dict['ind_comm_pub_reg_shareholder'], sub_json_dict['ind_comm_pub_reg_modify'] = self.analysis.parse_page_1(page, 'jibenxinxi')
                sub_json_dict['ind_comm_pub_arch_key_persons'], sub_json_dict['ind_comm_pub_arch_branch'], sub_json_dict['ind_comm_pub_arch_liquidation'] = self.analysis.parse_page_1(page, 'beian')
                sub_json_dict['ind_comm_pub_equity_ownership_reg'] = self.analysis.parse_page_1(page, 'guquanchuzi')
                sub_json_dict['ind_comm_pub_movable_property_reg'] = self.analysis.parse_page_1(page, 'dongchandiya')
                sub_json_dict['ind_comm_pub_business_exception'] = self.analysis.parse_page_1(page, 'jingyingyichang')
                sub_json_dict['ind_comm_pub_serious_violate_law'] = self.analysis.parse_page_1(page, 'yanzhongweifa')
                sub_json_dict['ind_comm_pub_spot_check'] = self.analysis.parse_page_1(page, 'chouchajiancha')
                sub_json_dict['ind_comm_pub_administration_sanction'] = self.analysis.parse_page_1(page, 'xingzhengchufa')
                pass
            elif types == 2:
                tabs = (
                        'entInfo',          # 登记信息
                        'curStoPleInfo',    #股权出质
                        'entCheckInfo',     #备案信息
                        'pleInfo',          #动产抵押登记信息
                        'cipPenaltyInfo',   #行政处罚
                        'cipUnuDirInfo',    #经营异常
                        'cipBlackInfo',     #严重违法
                        'cipSpotCheInfo',   #抽查检查
                        )

                div_names = (
                                'jibenxinxi',
                                'guquanchuzhi',
                                'beian',
                                'dongchandiya',
                                'xingzhengchufa',
                                'jingyingyichang',
                                'yanzhongweifa',
                                'chouchajiancha',
                            )
                for tab, div_name in zip(tabs, div_names):
                    #url = "http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=" + tab
                    url = urls['prefix_GSpublicity'] + tab
                    page = self.crawl_page_by_url_post(url, post_data)['page']
                    if div_name == 'jibenxinxi':
                        sub_json_dict['ind_comm_pub_reg_basic'], sub_json_dict['ind_comm_pub_reg_shareholder'], sub_json_dict['ind_comm_pub_reg_modify'] =  self.analysis.parse_page_2(page, div_name, post_data)
                    elif div_name == 'beian':
                        sub_json_dict['ind_comm_pub_arch_key_persons'], sub_json_dict['ind_comm_pub_arch_branch'], sub_json_dict['ind_comm_pub_arch_liquidation'] = self.analysis.parse_page_2(page, div_name, post_data)
                    elif div_name == 'guquanchuzhi':
                        sub_json_dict['ind_comm_pub_equity_ownership_reg'] = self.analysis.parse_page_2(page, div_name, post_data)
                    elif div_name == 'dongchandiya':
                        sub_json_dict['ind_comm_pub_movable_property_reg'] = self.analysis.parse_page_2(page, div_name, post_data)
                    elif div_name == 'xingzhengchufa':
                        sub_json_dict['ind_comm_pub_administration_sanction'] = self.analysis.parse_page_2(page, div_name, post_data)
                    elif div_name == 'jingyingyichang':
                        sub_json_dict['ind_comm_pub_business_exception'] = self.analysis.parse_page_2(page, div_name, post_data)
                    elif div_name == 'yanzhongweifa':
                        sub_json_dict['ind_comm_pub_serious_violate_law'] = self.analysis.parse_page_2(page, div_name, post_data)
                    elif div_name == 'chouchajiancha':
                        sub_json_dict['ind_comm_pub_spot_check'] = self.analysis.parse_page_2(page, div_name, post_data)
                    #json_dump_to_file("com_pub_2.json", sub_json_dict)

        except Exception as e:
            logger.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s, type is %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict



    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url, types, post_data={}):
        sub_json_dict = {}
        titles = (  'ent_pub_ent_annual_report',     # 企业年报
                    'ent_pub_shareholder_capital_contribution', # 企业投资人出资比例
                    'ent_pub_equity_change', # 股权变更信息
                    'ent_pub_administration_license', # 行政许可信息
                    'ent_pub_knowledge_property', # 知识产权出资登记
                    'ent_pub_administration_sanction', # 行政许可信息
                )
        try:
            if types == 0:
                page = self.crawl_page_by_url(url)['page']
                tables =  (
                                'qiyenianbao', #企业投资人出资比例
                                'xingzhengxuke', #股权变更信息
                                'xingzhengchufa',#行政处罚
                                'zhishichanquan', #知识产权出质登记信息
                                'touziren', # 股东及出资信息
                                'gudongguquan'# 股权变更信息
                            )
                for title, item in zip(titles, tables):
                    sub_json_dict[title] = self.analysis.parse_page(page, item)
            elif types == 1:
                page = self.crawl_page_by_url(url)['page']
                tables = (
                                'nianbao', # 企业年报
                                'touzirenjichuzi', #股东及出资信息
                                'zizhizigexuke', #行政许可
                                'xingzhengchufa',#行政处罚
                                'zhishichanquanchuzidengji', #知识产权出质登记信息
                                'guquanbiangeng'# 股权变更信息
                            )
                for title, item in zip(titles, tables):
                    sub_json_dict[title] = self.analysis.parse_page_1(page, item)
                pass
            elif types == 2:
                ent_pub_page_urls= {
                    "qiyenianbao" : "http://gsxt.gdgs.gov.cn/aiccips/BusinessAnnals/BusinessAnnalsList.html",  #企业年报
                    "sifapanding": "http://gsxt.gdgs.gov.cn/aiccips/ContributionCapitalMsg.html",  #股东及出资信息
                    "xzpun"     :   "http://gsxt.gdgs.gov.cn/aiccips/XZPunishmentMsg.html",         # 行政处罚
                    "appPer"    :   "http://gsxt.gdgs.gov.cn/aiccips/AppPerInformation.html",       #行政许可信息
                    "inproper"  :   "http://gsxt.gdgs.gov.cn/aiccips/intPropertyMsg.html",          #知识产权出质登记信息
                    "guquanbiangeng":   "http://gsxt.gdgs.gov.cn/aiccips/GDGQTransferMsg/shareholderTransferMsg.html",#股权变更信息
                }

                for (title, ids) in zip(titles, ent_pub_page_urls):
                    url = ent_pub_page_urls[ids]
                    page = self.crawl_page_by_url_post(url, post_data)['page']
                    sub_json_dict[title] = self.analysis.parse_page_2(page, ids, post_data)
                #json_dump_to_file("crawl_ent_pub_pages.json", sub_json_dict)
        except Exception as e:
            logger.debug(u"An error ocurred in crawl_ent_pub_pages: %s, types = %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict

    #爬取 其他部门公示信息 页面
    def crawl_other_dept_pub_pages(self, url, types, post_data={}):
        sub_json_dict={}
        titles =(   'other_dept_pub_administration_license',#行政许可信息
                    'other_dept_pub_administration_sanction',#行政处罚信息
                )
        try:
            if types==0:
                page = self.crawl_page_by_url(url)['page']
                tables= (   'xingzhengxuke',#行政许可信息
                                'xingzhengchufa'#行政处罚信息
                                )
                for title, item in zip(titles, tables):
                    sub_json_dict[title] = self.analysis.parse_page(page, item)
            elif types == 1:
                page = self.crawl_page_by_url(url)['page']
                tables= (
                                'zizhizigexuke', #资质资格许可信息
                                'xingzhengchufa', # 行政处罚信息
                    )
                for title, item in zip(titles, tables):
                    sub_json_dict[title] = self.analysis.parse_page_1(page, item)
            elif types== 2:
                other_dept_urls = {
                    "xzxk"  :   "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html",
                    "czcf"  :   "http://gsxt.gdgs.gov.cn/aiccips/OtherPublicity/environmentalProtection.html",
                    }
                for title, ids in zip(titles, other_dept_urls):
                    url = other_dept_urls[ids]
                    page = self.crawl_page_by_url_post(url, post_data)['page']
                    sub_json_dict[title] = self.analysis.parse_page_2(page, ids, post_data)
                #json_dump_to_file("crawl_other_dept_pub_pages.json", sub_json_dict)
        except Exception as e:
            logger.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s, types = %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict
        #json_dump_to_file("json_dict.json", self.json_dict)

    #judical assist pub informations
    def crawl_judical_assist_pub_pages(self, url, types, post_data={}):
        sub_json_dict={}
        titles = (  'judical_assist_pub_equity_freeze', # 股权冻结信息
                    'judical_assist_pub_shareholder_modify', #股东变更信息
                    )
        try:
            if types==0:
                pass
            elif types == 1:
                page = self.crawl_page_by_url(url)['page']
                tables = (
                        'guquandongjie',    #股权冻结信息
                        'gudongbiangeng',   #股东变更信息
                    )
                for title, item in zip(titles, tables):
                    sub_json_dict[title] = self.analysis.parse_page_1(page, item)
            elif types== 2:
                judical_assist_url = {
                    "guquandongjie"   :   "http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html",
                    "gudongbiangeng"  :   "http://gsxt.gdgs.gov.cn/aiccips/sfGuQuanChange/guQuanChange.html",
                    }

                for (title, ids) in zip(titles, judical_assist_url):
                    url = judical_assist_url[ids]
                    page = self.crawl_page_by_url_post(url, post_data)['page']
                    sub_json_dict[title] = self.analysis.parse_page_2(page, ids, post_data)
                #json_dump_to_file("crawl_judical_assist_pub_pages.json", sub_json_dict)
        except Exception as e:
            logger.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s, types = %d"% (type(e), types))
            raise e
        finally:
            return sub_json_dict
        pass

    def crawl_page_by_url(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            logger.error(u"Getting page by url:%s\n, return status %s\n"% (url, r.status_code))
            return False
        # 为了防止页面间接跳转，获取最终目标url
        return {'page' : r.text, 'url': r.url}

    def crawl_page_by_url_post(self, url, data, header={}):
        if header:
            r = self.requests.post(url, data, headers= header)
        else :
            r = self.requests.post(url, data)
        if r.status_code != 200:
            logger.error(u"Getting page by url with post:%s\n, return status %s\n"% (url, r.status_code))
            return False
        return {'page': r.text, 'url': r.url}

    # main function
    def work(self):
        ens = read_ent_from_file("./enterprise_list/guangdong1.txt")
        if not os.path.exists("./enterprise_crawler"):
            os.makedirs("./enterprise_crawler")
        for i, ent in enumerate(ens):
            self.crawl_page_search(urls['page_search'])
            self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent[2])
            self.analyze_showInfo()
            data = self.crawl_page_main()
            self.json_dict[ent[2]] = data
            json_dump_to_file("./enterprise_crawler/%s.json" % ent[0], self.json_dict)
            logger.debug(u"Now %s was finished\n"% ent[0])

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
            logger.debug(u"div.ul.li.a['href'] = %s\n", div.ul.li.a['href'])
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
    #获得表头
    def get_table_title(self, table_tag):
        if table_tag.find('tr'):
            if table_tag.find('tr').find_all('th') :
                if len(table_tag.find('tr').find_all('th')) > 1:
                    return None
                # 处理 <th> aa<span> bb</span> </th>
                if table_tag.find('tr').th.stirng == None and len(table_tag.find('tr').th.contents) > 1:
                    # 处理 <th>   <span> bb</span> </th>  包含空格的
                    if (table_tag.find('tr').th.contents[0]).strip()  :
                        return (table_tag.find('tr').th.contents[0])
                # <th><span> bb</span> </th>
                return self.get_raw_text_by_tag(table_tag.find('tr').th)
            elif table_tag.find('tr').find('td'):
                return self.get_raw_text_by_tag(table_tag.find('tr').td)
        return None

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
                logger.error('invalid multi_col_tag, multi_col_tag = %s', multi_col_tag)
                return data
            #数据表中会出现多出一空列的情况，fuck it。 要判断最后一列内容是否为空。
            tds = multi_col_tag.find_all('td', recursive = False)
            len_tds = len(tds)
            if not tds[len(tds)-1].get_text().strip() :
                len_tds= len_tds - 1
            if len(columns) != len_tds:
                logger.error('column head size != column data size, columns head = %s, columns data = %s' % (columns, multi_col_tag.contents))
                return data

            for id, col in enumerate(columns):
                data[col[0]] = self.get_column_data(col[1], tds[id])
            return data
        else:
            return self.get_raw_text_by_tag(td_tag)

    def get_detail_link(self, bs4_tag, prefix_url = ""):
        if bs4_tag['href'] and bs4_tag['href'] != '#':
            pattern = re.compile(r'http')
            if pattern.search(bs4_tag['href']):
                return bs4_tag['href']
            return prefix_url + bs4_tag['href']
        elif bs4_tag['onclick']:
            pattern = re.compile(r'http')
            if pattern.search(bs4_tag['onclick']):
                return self.get_detail_link_onclick(bs4_tag)
            return prefix_url + self.get_detail_link_onclick(bs4_tag)

    # type = 2 的详细报告的url
    def get_detail_link_onclick(self, bs4_tag):
        re1='.*?'   # Non-greedy match on filler
        re2='(\\\'.*?\\\')' # Single Quote String 1

        rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
        m = rg.search(bs4_tag['onclick'])
        url= ""
        if m:
            strng1=m.group(1)
            url = strng1.strip("\'")
        return url

    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            if len(bs_table.find_all('tbody')[0].find_all('tr')) >1:
                tbody = bs_table.find_all('tbody')[0]
            else :
                tbody= bs_table.find_all('tbody')[1]
        else:
            tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')

        tr = None
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                #tr = tbody.find('tr')
                return None
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
        #logger.debug(u"get_columns_of_record_table->tr:%s\n", tr)
        ret_val=  self.get_record_table_columns_by_tr(tr, table_name)
        #logger.debug(u"table columns:%s\n"% table_name)
        #logger.debug(u"ret_val->%s\n", ret_val)
        return  ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th'))==0:
                logger.error(u"The table %s has no columns"% table_name)
                return columns
            #排除仅仅出现一列重复的名字
            count = 0
            for i, th in enumerate(tr_tag.find_all('th')):
                col_name = self.get_raw_text_by_tag(th)
                #if col_name and ((col_name, col_name) not in columns) :

                if col_name:
                    if ((col_name, col_name) in columns) :
                        col_name= col_name+'_'
                        count+=1
                    if not self.sub_column_count(th):
                        columns.append((col_name, col_name))
                    else: #has sub_columns
                        columns.append((col_name, self.get_sub_columns(tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(th))))
                        sub_col_index += self.sub_column_count(th)
            if count == len(tr_tag.find_all('th'))/2:
                columns= columns[: len(columns)/2]

        except Exception as e:
            logger.error(u'exception occured in get_table_columns_by_tr, except_type = %s, table_name = %s' % (type(e), table_name))
        finally:
            return columns

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
                    logger.error(u'parse failed, with exception %s' % e)
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
                    if tr.find('td') and col_span == column_size and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'), urls['prefix_url_0'])

                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                    #html_to_file("next.html", detail_page['page'])
                                    if table_name == u'企业年报':
                                        #logger.debug(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')

                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page, table_name + '_detail')
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
                                next_url = self.get_detail_link(td.find('a'), urls['prefix_url_0'])
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)['page']

                                    if table_name == u'企业年报':
                                        #logger.debug(u"2next_url = %s, table_name= %s\n", next_url, table_name)

                                        page_data = self.parse_ent_pub_annual_report_page(detail_page, table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page, table_name + '_detail')
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
                    # 我给跪了，数据表无缘无故最后的多出一空列
                    elif tr.find('td') and len(tr.find_all('td', recursive=False)) == col_span+1 and col_span != column_size:
                        col_count = 0
                        sub_col_index = 0
                        item = {}
                        sub_item = {}
                        tds = tr.find_all('td',recursive=False)[:-1]
                        for i, td in enumerate(tds):
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
                            logger.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
        except Exception as e:
            logger.error(u'parse table %s failed with exception %s， types= 0' % (table_name, type(e)))
            raise e
        finally:
            return table_dict

    # 第一种类型的年报页面
    def parse_ent_pub_annual_report_page(self, page_dict, table_name):
        url = page_dict['url']
        page = page_dict['page']
        page_data= {}
        soup = BeautifulSoup(page, "html5lib")
        number = len(soup.find('ul', {'id': 'ContentPlaceHolder1_ulTag'}).find_all('li'))
        if number == 0 :
            logger.error(u"Could not find tab in annual report page")
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
            logger.error(u'Could not get response page')
            return False
        page = r.text
        #html_to_file("annual.html", page)
        table_name = ""
        try:
            soup = BeautifulSoup(page, 'html5lib')
            content_table = soup.find_all('table')[1:]
            for table in content_table:
                table_name = self.get_table_title(table)
                #logger.debug(u"annual report table_name= %s\n", table_name)
                table_data = self.parse_report_table(table, table_name)
                page_data[table_name] = table_data
        except Exception as e:
            logger.error(u'annual page: fail to get table data with exception %s' % e)
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
                logger.error(u'Could not get response page')
                return False
            page = r.text
            #html_to_file("annual.html", page)
            table_name = ""
            try:
                soup = BeautifulSoup(page, 'html5lib')
                content_table = soup.find_all('table')[1:]
                for table in content_table:
                    table_name = self.get_table_title(table)
                    #logger.debug(u"annual report table_name= %s\n", table_name)
                    table_data = self.parse_report_table(table, table_name)
                    #json_dump_to_file('report_json.json', table_data)
                    page_data[table_name] = table_data

            except Exception as e:
                logger.error(u'annual page: fail to parse page with exception %s'%e)
                raise e
        #json_dump_to_file('report_json.json', page_data)
        return page_data
    #   分析第0种情况的年度报表
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

    # 如果是第二种： http://gsxt.gdgs.gov.cn/aiccips/ q情况
    def parse_ent_pub_annual_report_page_2(self, base_page, page_type):

        page_data = {}
        soup = BeautifulSoup(base_page, 'html5lib')
        if soup.body.find('table'):
            try:
                base_table = soup.body.find('table')
                table_name = u'企业基本信息'#self.get_table_title(base_table)
                #这里需要连续两个nextSibling，一个nextSibling会返回空
                detail_base_table = base_table.nextSibling.nextSibling
                if detail_base_table.name == 'table':
                    page_data[table_name] = self.parse_table_2(detail_base_table )
                    pass
                else:
                    logger.error(u"Can't find details of base informations for annual report")
            except Exception as e:
                logger.error(u"fail to get table name with exception %s" % (type(e)))
            try:
                table = detail_base_table.nextSibling.nextSibling
                while table:
                    if table.name == 'table':
                        table_name = self.get_table_title(table)
                        page_data[table_name] = []
                        columns = self.get_columns_of_record_table(table, base_page, table_name)
                        page_data[table_name] =self.parse_table_2(table, columns, {}, table_name)
                    table = table.nextSibling
            except Exception as e:
                logger.error(u"fail to parse the rest tables with exception %s" %(type(e)))
        else:
            pass
        return page_data


    def parse_page_data_2(self, page):
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
            data['entType'] = soup.find("input", {"id": "entType"})['value'].strip()+"++"
            data['regOrg'] = soup.find("input", {"id": "regOrg"})['value']

        except Exception as e:
            logger.error(u"parse page failed in function parse_page_data_2\n" )
            raise e
        finally:
            return data

    # 如果是第一种： http://121.8.226.101:7001/search/search!annalShow?annalVo.id=30307309
    def parse_ent_pub_annual_report_page_1(self, base_page, page_type):
        page_data = {}
        soup = BeautifulSoup(base_page, 'html5lib')
        if soup.body.find('table'):
            try:
                #忽略第一行tr
                detail_base_table = soup.body.find('table').find_all('tr')[1:]
                table_name = self.get_raw_text_by_tag(detail_base_table[0])
                sub_dict = {}
                for tr in detail_base_table[1:]:
                    if tr.find('th') and tr.find('td'):
                        ths = tr.find_all('th')
                        tds = tr.find_all('td')
                        if len(ths) != len(tds):
                            logger.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    sub_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])

                page_data[table_name] = sub_dict
            except Exception as e:
                logger.error(u"fail to get table name with exception %s" % (type(e)))
            try:
                tables = soup.body.find_all('table')[1:]
                for table in tables:
                    table_name = self.get_table_title(table)
                    page_data[table_name] = []
                    columns = self.get_columns_of_record_table(table, base_page, table_name)
                    page_data[table_name] =self.parse_table_1(table, columns, {}, table_name)
            except Exception as e:
                logger.error(u"fail to parse the rest tables with exception %s" %(type(e)))
        else:
            pass
        return page_data

    def parse_page_1(self, page, div_id, post_data={}):
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
                        if div_id == 'jibenxinxi':
                            table = divs.find('div').find('table')
                            table_name = self.get_table_title(table)
                            print table_name
                            if table_name== None :
                                table_name = div_id
                            page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            page_data[table_name] =self.parse_table_1(table, columns, post_data, table_name)
                            table = divs.find('table', recursive = False)
                        else:
                            table = divs.find('table')
                    #print table
                    table_name = ""
                    columns = []
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            if table_name== None :
                                table_name = div_id
                            #page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            if columns is not  None:
                                page_data[table_name] =self.parse_table_1(table, columns, post_data, table_name)
                        table = table.nextSibling

                except Exception as e:
                    logger.error(u'parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_table_1(self, bs_table, columns=[] , post_data= {}, table_name= ""):
        table_dict = None
        try:
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
                # 这里注意unicode编码
                next_dicts = {
                    u"主要人员信息" : "http://121.8.226.101:7001/search/search!staffListShow?entityVo.pageSize=10&entityVo.curPage=%d&entityVo.pripid=%s",
                    u"分支机构信息":  "http://121.8.226.101:7001/search/search!branchListShow?_=1451527284000&entityVo.curPage=%d&entityVo.pripid=%s",
                    u"出资人及出资信息": "http://121.8.226.101:7001/search/search!investorListShow?_=1451527307501&entityVo.curPage=%d&entityVo.pripid=%s",
                    u"变更信息" : "http://121.8.226.101:7001/search/search!changeListShow?_=1451527321304&entityVo.curPage=%d&entityVo.pripid=%s",
                }
                if next_dicts.has_key(table_name) and post_data :
                    url = next_dicts[table_name]%(1,  post_data['pripid'])
                    res = self.crawler.crawl_page_by_url(url)['page']
                    d = json.loads(res)
                    totalPage = int(d['baseVo']['totalPage'])
                    data_list = []

                    titles = [column[0] for column in columns]
                    if table_name == u"主要人员信息":
                        for i in xrange(totalPage):
                            url = next_dicts[table_name]%(i + 1,  post_data['pripid'])
                            res = self.crawler.crawl_page_by_url(url)['page']
                            d = json.loads(res)
                            data_list.extend([item for item in d['staffList']])
                        for i, model in enumerate(data_list):
                            data = [i+1, model['name'], model['sdutyname']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"分支机构信息":
                        for i in xrange(totalPage):
                            url = next_dicts[table_name]%(i + 1,  post_data['pripid'])
                            res = self.crawler.crawl_page_by_url(url)['page']
                            d = json.loads(res)
                            data_list.extend([item for item in d['branchList']])
                        for i, model in enumerate(data_list):
                            data = [i+1, model['branchregno'], model['branchentname'], model['sregorgname']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"出资人及出资信息":
                        for i in xrange(totalPage):
                            url = next_dicts[table_name]%(i + 1,  post_data['pripid'])
                            res = self.crawler.crawl_page_by_url(url)['page']
                            d = json.loads(res)
                            data_list.extend([item for item in d['investorList']])
                        for i, model in enumerate(data_list):
                            data = [ model['sinvenstorname'], model['inv'], model['cardname'], model['cerno']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"变更信息":
                        for i in xrange(totalPage):
                            url = next_dicts[table_name]%(i + 1,  post_data['pripid'])
                            res = self.crawler.crawl_page_by_url(url)['page']
                            d = json.loads(res)
                            data_list.extend([item for item in d['changeList']])
                        for i, model in enumerate(data_list):
                            data = [ model['sname'], model['altbe'], model['altaf'], model['altdate']]
                            item_array.append(dict(zip(titles, data)))
                    table_dict = item_array
                else:
                    if not tbody:
                        #records_tag = bs_table
                        records_tag = bs_table
                    else:
                        records_tag = tbody
                    for tr in records_tag.find_all('tr'):
                        if tr.find('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                            col_count = 0
                            item = {}
                            for td in tr.find_all('td',recursive=False):
                                if td.find('a'):
                                    next_url = self.get_detail_link(td.find('a'), urls['prefix_url_1'])
                                    #has detail link
                                    if next_url:
                                        detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                        #html_to_file("next.html", detail_page['page'])
                                        if table_name == u'基本信息':
                                            page_data = self.parse_ent_pub_annual_report_page_1(detail_page, table_name+ '_detail')
                                        else:
                                            page_data = self.parse_page_1(detail_page, table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                else:
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                col_count += 1
                                if col_count == column_size:
                                    item_array.append(item.copy())
                                    col_count = 0
                        #this case is for the ind-comm-pub-reg-shareholders----details'table
                        elif tr.find('td') and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
                            col_count = 0
                            sub_col_index = 0
                            item = {}
                            sub_item = {}
                            for td in tr.find_all('td',recursive=False):
                                if td.find('a'):
                                    #try to retrieve detail link from page
                                    next_url = self.get_detail_link(td.find('a'), urls['prefix_url_1'])
                                    #has detail link
                                    if next_url:
                                        detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                        if table_name == u'基本信息':
                                            page_data = self.parse_ent_pub_annual_report_page_1(detail_page, table_name+ '_detail')
                                        else:
                                            page_data = self.parse_page_1(detail_page, table_name + '_detail')
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
                            logger.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
        except Exception as e:
            logger.error(u'parse table %s failed with exception %s' % (table_name, type(e)))
            raise e
        finally:
            return table_dict


    def parse_page_2(self, page, div_id, post_data={}):
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
                    columns = []
                    while table:
                        if table.name == 'table':
                            table_name = self.get_table_title(table)
                            if table_name== None :
                                table_name = div_id
                            page_data[table_name] = []
                            columns = self.get_columns_of_record_table(table, page, table_name)
                            page_data[table_name] =self.parse_table_2(table, columns, post_data, table_name)

                        elif table.name == 'div':
                            if not columns:
                                logger.error(u"Can not find columns when parsing page 2, table :%s"%div_id)
                                break
                            page_data[table_name] =  self.parse_table_2(table, columns, post_data, table_name)
                            columns = []
                        table = table.nextSibling


                except Exception as e:
                    logger.error(u'parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_table_2(self, bs_table, columns=[] , post_data= {}, table_name= ""):
        table_dict = None
        try:
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
                # <div> <table>数据</table><table>下一页</table> </div>
                tables = bs_table.find_all('table')
                # 对于types = 2的情况。
                if len(tables)==2 and tables[1].find('a'):
                    # 获取下一页的url
                    clickstr = tables[1].find('a')['onclick']

                    re1='.*?'   # Non-greedy match on filler
                    re2='\\\'.*?\\\''   # Uninteresting: strng
                    re3='.*?'   # Non-greedy match on filler
                    re4='(\\\'.*?\\\')' # Single Quote String 1
                    re5='.*?'   # Non-greedy match on filler
                    re6='(\\\'.*?\\\')' # Single Quote String 2

                    rg = re.compile(re1+re2+re3+re4+re5+re6,re.IGNORECASE|re.DOTALL)
                    m = rg.search(clickstr)
                    url = ""
                    if m:
                        string1=m.group(1)
                        string2=m.group(2)
                        url = string1.strip('\'')+string2.strip('\'')
                        logger.debug(u"url = %s\n" % url)
                    data = {
                        "pageNo" : "2",
                        "entNo" : post_data["entNo"],
                        "regOrg" : post_data["regOrg"],
                        "entType" : post_data["entType"],
                    }
                    res = self.crawler.crawl_page_by_url_post(url, data, {'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',})
                    #print res['page']
                    if table_name == u"变更信息":
                        # chaToPage
                        d = json.loads(res['page'])
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [model['altFiledName'], model['altBe'], model['altAf'], model['altDate']]
                            item_array.append(dict(zip(titles, data)))
                    elif table_name == u"主要人员信息":
                        # vipToPage
                        d = json.loads(res['page'], encoding="utf-8")
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [ i+1, model['name'], model['position']]
                            item_array.append(dict(zip(titles, data)))

                    elif table_name == u"分支机构信息":
                        #braToPage
                        d = json.loads(res['page'])
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [ i+1, model['regNO'], model['brName'].encode('utf8').decode('utf8'), model['regOrg'].encode('utf8')]
                            item_array.append(dict(zip(titles, data)))

                    elif table_name == u"股东信息":
                        print "股东信息"
                        d = json.loads(res['page'])
                        titles = [column[0] for column in columns]
                        for i, model in enumerate(d['list']):
                            data = [ model['invType'], model['inv'], model['certName'], mode['certNo']]
                            item_array.append(dict(zip(titles, data)))

                    table_dict = item_array

                else:

                    if not tbody:
                        #records_tag = bs_table
                        records_tag = tables[0]
                    else:
                        records_tag = tbody
                    for tr in records_tag.find_all('tr'):
                        if tr.find('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                            col_count = 0
                            item = {}
                            for td in tr.find_all('td',recursive=False):
                                if td.find('a'):
                                    next_url = self.get_detail_link(td.find('a'), urls['prefix_url_0'])
                                    #has detail link
                                    if next_url:
                                        detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                        if table_name == u'qiyenianbao':
                                            page_data = self.parse_ent_pub_annual_report_page_2(detail_page, table_name+ '_detail')
                                        else:
                                            page_data = self.parse_page_2(detail_page, table_name + '_detail')
                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                else:
                                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                                col_count += 1
                                if col_count == column_size:
                                    item_array.append(item.copy())
                                    col_count = 0
                        #this case is for the ind-comm-pub-reg-shareholders----details'table
                        elif tr.find('td') and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
                            col_count = 0
                            sub_col_index = 0
                            item = {}
                            sub_item = {}
                            for td in tr.find_all('td',recursive=False):
                                if td.find('a'):
                                    #try to retrieve detail link from page
                                    next_url = self.get_detail_link(td.find('a'), urls['prefix_url_0'])
                                    #has detail link
                                    if next_url:
                                        detail_page = self.crawler.crawl_page_by_url(next_url)['page']
                                        if table_name == u'qiyenianbao':
                                            page_data = self.parse_ent_pub_annual_report_page_2(detail_page, table_name+ '_detail')
                                        else:
                                            page_data = self.parse_page_2(detail_page, table_name + '_detail')
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
                            logger.error(u'th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if self.get_raw_text_by_tag(ths[i]):
                                    table_dict[self.get_raw_text_by_tag(ths[i])] = self.get_raw_text_by_tag(tds[i])
        except Exception as e:
            logger.error(u'parse table %s failed with exception %s' % (table_name, type(e)))
            raise e
        finally:
            return table_dict


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
        logger.error(u"There is no path : %s"% path )
    lines = []
    with codecs.open(path, read_type, 'utf-8') as f:
        lines = f.readlines()
    lines = [ line.split(',') for line in lines ]
    return lines

def html_from_file(path):
    read_type = 'r'
    if not os.path.exists(path):
        return None
    datas = None
    with codecs.open(path, read_type, 'utf8') as f:
        datas = f.read()
        f.close()
    return datas


class GuangdongClawer(object):
    def __init__(self):
        self.analysis = Analyze()
        self.crawler = Crawler(self.analysis)
        self.analysis.crawler = self.crawler

    def run(self):
        self.crawler.work()


if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    guangdong = GuangdongClawer()
    guangdong.run()

