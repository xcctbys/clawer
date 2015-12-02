#!/usr/bin/env python
#encoding=utf-8
import os
import time
import re
import urllib
import unittest
import logging
import settings
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import CrawlerUtils
from crawler import CheckCodeCracker

DEBUG=True

class CrawlerBeijingEnt(Crawler):
    html_restore_path = settings.html_restore_path + '/Beijing/'
    json_restore_path = settings.json_restore_path + '/Beijing/'
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
        from beijing_hparser import ParserBeijingEnt as Parser
        self.parser = Parser(self)
        self.credit_ticket = None


    def crawl_check_page(self):
        count = 0
        while True:
            count += 1
            ckcode = self.crack_checkcode()
            post_data = self.generate_ckcode_post(currentTimeMillis=self.time_stamp, credit_ticket = self.credit_ticket, checkcode = ckcode, keyword = self.ent_number);
            next_url = CrawlerBeijingEnt.urls['post_checkcode']
            page = self.opener.open(next_url, data = urllib.urlencode(post_data)).read()
            time.sleep(1)
            crack_result = self.parse_post_check_page(page)
            if crack_result:
                break
            else:
                logging.debug('crack checkcode failed, total faiil count = %d' % count)

    #ind-comm_pub information
    def crawl_ind_comm_pub_pages(self):
        for item in ('ind_comm_pub_reg_basic',          # 登记信息-基本信息
                     'ind_comm_pub_reg_shareholder',   # 股东信息
                     'ind_comm_pub_reg_modify',
                     'ind_comm_pub_arch_key_persons',  # 备案信息-主要人员信息
                     'ind_comm_pub_arch_branch',      # 备案信息-分支机构信息
                     'ind_comm_pub_arch_liquidation', # 备案信息-清算信息
                     'ind_comm_pub_movable_property_reg', # 动产抵押登记信息
                     'ind_comm_pub_equity_ownership_reg', # 股权出置登记信息
                     'ind_comm_pub_administration_sanction', # 行政处罚信息
                     'ind_comm_pub_business_exception',  # 经营异常信息
                     'ind_comm_pub_serious_violate_law',  # 严重违法信息
                     'ind_comm_pub_spot_check'):        # 抽查检查信息

            page = self.get_page(item, 1)
            pages = self.get_all_pages_of_a_section(page, item)
            if len(pages) == 1:
                self.json_dict[item] = self.parser.parse_page(page, item)
            else:
                self.json_dict[item] = []
                for p in pages:
                    self.json_dict[item] += self.parser.parse_page(p, item)

    #enterprise pub informations
    def crawl_ent_pub_pages(self):
        for item in (
                    'ent_pub_shareholder_capital_contribution', #企业投资人出资比例
                    'ent_pub_equity_change', #股权变更信息
                    'ent_pub_administrative_license',#行政许可信息
                    'ent_pub_knowledge_property', #知识产权出资登记
                    'ent_pub_administration_sanction' #行政许可信息
                    ):
            page = self.get_page(item, 2)
            pages = self.get_all_pages_of_a_section(page, item)

            if len(pages) == 1:
                self.json_dict[item] = self.parser.parse_page(page, item)
            else:
                self.json_dict[item] = []
                for p in pages:
                    self.json_dict[item] += self.parser.parse_page(p, item)

    #other department pub informations
    def crawl_other_dept_pub_pages(self):
        for item in ('other_dept_pub_administrative_license',#行政许可信息
                    'other_dept_pub_administrative_sancrtion'#行政处罚信息
        ):
            page = self.get_page(item, 3)
            pages = self.get_all_pages_of_a_section(page, item)

            if len(pages) == 1:
                self.json_dict[item] = self.parser.parse_page(page, item)
            else:
                self.json_dict[item] = []
                for p in pages:
                    self.json_dict[item] += self.parser.parse_page(p, item)

    #judical assist pub informations
    def crawl_judical_assist_pub_pages(self):
        pass

    #crack the checkcode
    def crack_checkcode(self):
        checkcode_url =  self.get_checkcode_url()
        page = self.opener.open(checkcode_url).read()
        with open(self.ckcode_image_path, 'w') as f:
            f.write(page)
        return self.ck_cracker.crack(self.ckcode_image_path)


    def get_checkcode_url(self):
        while True:
            response = self.opener.open(CrawlerBeijingEnt.urls['official_site']).read()
            time.sleep(1)
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

    #generate post data for submit checkcode and other necessary information
    def generate_ckcode_post(self, **args):
        post_data = {}
        post_data['currentTimeMillis'] = args['currentTimeMillis']
        post_data['credit_ticket'] = args['credit_ticket']
        post_data['checkcode'] = args['checkcode']
        post_data['keyword'] = args['keyword']
        return post_data

    #parse the page appears after we submit the checkcode
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

    #parse the page appears before we submit the checkcode
    def parse_pre_check_page(self, page):
         soup = BeautifulSoup(page)
         ckimg_src= soup.find_all('img', id='MzImgExpPwd')[0].get('src')
         ckimg_src = str(ckimg_src)
         re_currenttime_millis=re.compile(r'/CheckCodeCaptcha\?currentTimeMillis=([\s\S]*)')
         self.credit_ticket = soup.find_all('input',id='credit_ticket')[0].get('value')
         self.time_stamp= re_currenttime_millis.findall(ckimg_src)[0]


    def crawl_page_by_url(self, url):
        page = self.opener.open(url).read()
        time.sleep(1)
        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.html_restore_path + 'detail.html', page)
        return page

    #there may be several pages in a section, get all these pages together, simplifying our parse job
    def get_all_pages_of_a_section(self, page, type):
        soup = BeautifulSoup(page)
        page_count = 0
        page_size = 0
        pages_data = []
        pages_data.append(page)
        r1 = soup.find_all('input', {'type':'hidden', 'id':'pagescount'})
        r2 = soup.find_all('input', {'type':'hidden', 'id':'pageSize', 'name':'pageSize'})
        if r1 and r2:
            page_count = int(r1[0].get('value'))
            page_size = int(r2[0].get('value'))
        else:
            #only has one page, do not need to crawl other pages
            return pages_data

        if page_count <= 1:
            #only has one page, do not need to crawl other pages
            return pages_data

        next_url = CrawlerBeijingEnt.urls[type].rstrip('?')
        for p in range(1, page_count):
            post_data={'pageNos':str(p+1), 'clear':'', 'pageNo':str(p), 'pageSize':str(page_size), 'ent_id':self.ent_id}
            try:
                page = self.opener.open(next_url, data=urllib.urlencode(post_data)).read()
                time.sleep(1)
            except Exception as e:
                logging.error('open new tab page failed, url = %s, page_num = %d' % (next_url, p+1))
                page = None
            finally:
                if page:
                    #more than one page display the same form, we should insert these pages into json
                    #should guarantee that the parse result is a list of items
                    pages_data.append(page)
        return pages_data

    #get page, add all the possible information after the url, just for simplicity.
    #tab refers to the three types of information, 1 ind_comm_pub_information, 2 enterprise_pub information, 3 other department pub information
    def get_page(self, type, tab):
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
        time.sleep(1)

        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.html_restore_path + type + '.html', page)
        return page

    def generate_time_stamp(self):
        return int(time.time())
'''
class TestCrawlwerBeijingEnt(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_crawl_work(self):
        self.crawler = CrawlerBeijingEnt(CheckCodeCracker())
        self.crawler.crawl_work('110000450096015')
'''
if __name__ == '__main__':
    CrawlerUtils.set_logging(settings.log_level)
    crawler = CrawlerBeijingEnt(CheckCodeCracker())
    #enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/beijing.txt')
    enterprise_list = ['110000450096015']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        logging.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.crawl_work(ent_number = ent_number)
