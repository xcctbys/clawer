#!/usr/bin/env python
#encoding=utf-8
import os
import time
import re
import urllib
import unittest
import logging

from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import CrawlerUtils
from crawler import CheckCodeCracker
from beijing_analyzer import AnalyzerBeijingEnt as Analyzer

DEBUG=True

class CrawlerBeijingEnt(Crawler):
    page_restore_dir = './htmls/Beijing/'
    urls = {'host':'http://qyxy.baic.gov.cn',
            'official_site': 'http://qyxy.baic.gov.cn/beijing',
            'get_checkcode': 'http://qyxy.baic.gov.cn',
            'post_checkcode': 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!getBjQyList.dhtml',
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
    def __init__(self, ck_cracker):
        super(self.__class__, self).__init__(ck_cracker)
        self.credit_ticket = None

    def crawl_check_page(self):
        count = 0
        while True:
            count += 1
            ckcode = self.crack_checkcode()
            post_data = self.generate_ckcode_post(currentTimeMillis=self.time_stamp, credit_ticket = self.credit_ticket, checkcode = ckcode, keyword = ent_number);
            next_url = CrawlerBeijingEnt.urls['post_checkcode']
            page = self.opener.open(next_url, data = urllib.urlencode(post_data)).read()
            crack_result = self.parse_post_check_page(page)
            if crack_result:
                break
            else:
                logging.debug('crack checkcode failed, total faiil count = %d' % count)



    #工商公示信息
    def crawl_ind_comm_pub_pages(self):
        for item in ('ind_comm_pub_reg_basic',#登记信息-基本信息
                     'ind_comm_pub_reg_shareholder', #股东信息
                     'ind_comm_pub_reg_modify',  #登记信息-变更信息
                     'ind_comm_pub_arch_key_persons', #备案信息-主要人员信息
                     'ind_comm_pub_arch_branch', #备案信息-分支机构信息
                     'ind_comm_pub_arch_liquidation', #备案信息-清算信息
                     'ind_comm_pub_movable_property_reg',#动产抵押登记信息
                     'ind_comm_pub_equity_ownership_reg', #股权出置登记信息
                     'ind_comm_pub_administration_sanction', #行政处罚信息
                     'ind_comm_pub_business_exception',  #经营异常信息
                     'ind_comm_pub_serious_violate_law',  #严重违法信息
                     'ind_comm_pub_spot_check'):#抽查检查信息

            page = self.get_page(item, 1, False)
            self.crawl_page_tabs(page, item)

    #企业公示信息
    def crawl_ent_pub_pages(self):
        #企业年报信息
        page = self.get_page('ent_pub_ent_annual_report', 2)
        self.crawl_ent_annual_report(page)

        for item in (
                    'ent_pub_shareholder_capital_contribution', #企业投资人出资比例
                    'ent_pub_equity_change', #股权变更信息
                    'ent_pub_administrative_license',#行政许可信息
                    'ent_pub_knowledge_property', #知识产权出资登记
                    'ent_pub_administration_sanction' #行政许可信息
                    ):
            self.get_page(item, 2)

    #其他部门公示信息
    def crawl_other_dept_pub_pages(self):
        for item in ('other_dept_pub_administrative_license',#行政许可信息
                    'other_dept_pub_administrative_sancrtion'#行政处罚信息
        ):
            self.get_page(item, 3)

    #司法协助公示信息
    def crawl_judical_assist_pub_pages(self):
        pass

    #破解验证码
    def crack_checkcode(self):
        checkcode_url =  self.get_checkcode_url()
        page = self.opener.open(checkcode_url).read()
        with open(self.ckcode_image_path, 'w') as f:
            f.write(page)
        return self.ck_cracker.crack(self.ckcode_image_path)


    def get_checkcode_url(self):
        while True:
            response = self.opener.open(CrawlerBeijingEnt.urls['official_site']).read()
            soup = BeautifulSoup(response)
            ckimg_src= soup.find_all('img', id='MzImgExpPwd')[0].get('src')
            ckimg_src = str(ckimg_src)
            re_checkcode_captcha=re.compile(r'/([\s\S]*)\?currentTimeMillis')
            re_currenttime_millis=re.compile(r'/CheckCodeCaptcha\?currentTimeMillis=([\s\S]*)')
            checkcode_type = re_checkcode_captcha.findall(ckimg_src)[0]

            if checkcode_type == 'CheckCodeCaptcha':
                checkcode_url= CrawlerBeijingEnt.urls['get_checkcode'] + ckimg_src
                #parse the pre check page, get useful information
                self.parse_pre_check_page(response)
                return checkcode_url
            logging.debug('get crackable checkcode img failed')
        return None

    #生成验证码 post
    def generate_ckcode_post(self, **args):
        post_data = {}
        post_data['currentTimeMillis'] = args['currentTimeMillis']
        post_data['credit_ticket'] = args['credit_ticket']
        post_data['checkcode'] = args['checkcode']
        post_data['keyword'] = args['keyword']
        return post_data

    #解析提交验证码之后的页面
    def parse_post_check_page(self, page):
        if page == 'fail':
             logging.error('checkcode submitted error!')
             return False
        soup = BeautifulSoup(page)
        r = soup.find_all('a', {'href':"#", 'onclick' : re.compile(r'openEntInfo')})

        ent = ''
        if r:
            ent = r[0]['onclick']
        else:
            logging.debug('fail to find openEntInfo')

        m = re.search(r'\'([\w]*)\'[ ,]+\'([\w]*)\'[ ,]+\'([\w]*)\'', ent)
        if m:
            self.ent_id = m.group(1)
            self.credit_ticket = m.group(3)

        r = soup.find_all('input', {'type':"hidden", 'name':"currentTimeMillis", 'id':"currentTimeMillis"})
        if r:
            self.time_stamp = r[0]['value']
        else:
            logging.debug('fail to get time stamp')
        return True

    #解析提交验证码之前的页面
    def parse_pre_check_page(self, page):
         soup = BeautifulSoup(page)
         ckimg_src= soup.find_all('img', id='MzImgExpPwd')[0].get('src')
         ckimg_src = str(ckimg_src)
         re_currenttime_millis=re.compile(r'/CheckCodeCaptcha\?currentTimeMillis=([\s\S]*)')
         self.credit_ticket = soup.find_all('input',id='credit_ticket')[0].get('value')
         self.time_stamp= re_currenttime_millis.findall(ckimg_src)[0]


    #爬取投资人详情信息
    def crawl_shareholder_details(self, page):
        soup = BeautifulSoup(page)
        shareholders = soup.find_all('a', {'href':'javascript:void(0);', 'onclick':re.compile(r'viewInfo')})
        count = 0
        for item in shareholders:
            m = re.search(r'viewInfo\(\'([\w]*)\'\)', item.get('onclick'))
            try:
                shid = m.group(1)
            except:
                logging.debug('fail to find shareholder id')
            finally:
                if shid:
                    count += 1
                    next_url = CrawlerUtils.add_params_to_url(CrawlerBeijingEnt.urls['shareholder_detail'], {'chr_id':shid, 'entName':'', 'fqr':'','timeStamp':self.generate_time_stamp()})
                    logging.info('get shareholder detail, url:\n%s\n' % next_url)
                    page = self.opener.open(next_url).read()
                    CrawlerUtils.save_page_to_file(self.page_restore_dir + 'shareholder_detail_%d.html' % count, page)

    #爬取企业年报
    def crawl_ent_annual_report(self, page):
        soup = BeautifulSoup(page)
        reports = soup.find_all('a', {'target' : '_blank', 'href': re.compile(r'/qynb/entinfoAction!qynbxx\.dhtml\?cid=')})
        if reports:
            for item in reports:
                year = item.string
                href = item.get('href')
                self.deep_crawl_ent_annual_report(year, href)


    #企业年报中包含多个连接，需要深入爬取
    def deep_crawl_ent_annual_report(self, year, href):
        next_url = CrawlerBeijingEnt.urls['host'] + href
        base_page = self.opener.open(next_url).read()
        CrawlerUtils.save_page_to_file(self.page_restore_dir + 'annual_report_%s_base_info.html' % year, base_page)
        report_items = {'wzFrame' : 'website_info', 'gdczFrame':'shareholder_contribute_info', 'dwdbFrame' : 'external_guarantee_info', 'xgFrame':'modify_record_info'}
        for item in report_items.items():
            pat = re.compile(r'<iframe +id="%s" +src=\'(/entPub/entPubAction!.+)\'' % item[0])
            m = pat.search(base_page)
            if m:
                next_url = CrawlerBeijingEnt.urls['host'] + m.group(1)
                logging.info('get annual report, url:\n%s\n' % next_url)
                page = self.opener.open(next_url).read()
                CrawlerUtils.save_page_to_file(self.page_restore_dir + 'annual_report_%s_%s.html' % (year, item[1]), page)

    #判断一个页面中是否含有详情连接
    def has_detail_link(self, page):
        if page.find('详情') >= 0 and page.find('onclick="viewInfo(') >= 0:
            return True
        return False

    #某些页面含有‘详情’链接
    def crawl_detail(self,page,type):
        #暂时只看到 股东信息 中含有 详情连接
        if type == 'ind_comm_pub_reg_shareholder':
            self.crawl_shareholder_details(page)
        else:
            logging.error('missing %s detail link to crawl' % type)

    #有些信息分了多页显示，通过上一页、下一页按钮进行跳转
    def crawl_page_tabs(self, page, type):
        soup = BeautifulSoup(page)
        page_count = 0
        page_size = 0
        r1 = soup.find_all('input', {'type':'hidden', 'id':'pagescount'})
        r2 = soup.find_all('input', {'type':'hidden', 'id':'pageSize', 'name':'pageSize'})
        if r1 and r2:
            page_count = int(r1[0].get('value'))
            page_size = int(r2[0].get('value'))
        else:
            CrawlerUtils.save_page_to_file(self.page_restore_dir + type + '.html', page)
            if self.has_detail_link(page):
                self.crawl_detail(page, type)
            return

        if page_count <= 1:
            CrawlerUtils.save_page_to_file(self.page_restore_dir + type + '.html', page)
            if self.has_detail_link(page):
                self.crawl_detail(page, type)
            return

        next_url = CrawlerBeijingEnt.urls[type].rstrip('?')
        for p in range(1, page_count):
            CrawlerUtils.save_page_to_file(self.page_restore_dir + type + '_page_%d.html' % p, page)
            post_data={'pageNos':str(p+1), 'clear':'', 'pageNo':str(p), 'pageSize':str(page_size), 'ent_id':self.ent_id}
            try:
                page = self.opener.open(next_url, data=urllib.urlencode(post_data)).read()
            except:
                logging.error('open new tab page failed, url = %s, page_num = %d' % (next_url, p+1))
                page = None
            finally:
                if page:
                    CrawlerUtils.save_page_to_file(self.page_restore_dir + type + '_page_%d.html' % (p+1), page)
                    if self.has_detail_link(page):
                        self.crawl_detail(page, type)


    #获取页面，即使有些页面不需要这么多的GET 参数，为了简化，也给加了进去，其中 tab表示tab页面
    #1 对应工商公示信息， 2对应企业公示信息， 3 对应其他部门公示信息
    def get_page(self, type, tab, save=True):
        url = CrawlerUtils.add_params_to_url(CrawlerBeijingEnt.urls[type],
                                            {'entId':self.ent_id,
                                             'ent_id':self.ent_id,
                                             'entid':self.ent_id,
                                            'credit_ticket':self.credit_ticket,
                                            'entNo':self.ent_number,
                                            'entName':'',
                                            'timeStamp':self.generate_time_stamp(),
                                            'clear':'true',
                                            'str':tab
                                            })
        logging.info('get %s, url:\n%s\n' % (type, url))
        page = self.opener.open(url).read()
        #默认直接存到文件中
        if save:
            CrawlerUtils.save_page_to_file(self.page_restore_dir + type + '.html', page)
        return page

    def generate_time_stamp(self):
        return int(time.time())

class TestCrawlerBeijingEnt(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_crawl_page_tabs(self):
        pass

if __name__ == '__main__':
    CrawlerUtils.set_logging(DEBUG)
    crawler = CrawlerBeijingEnt(CheckCodeCracker())
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/beijing.txt')
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        logging.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.crawl_work(ent_number = ent_number)
