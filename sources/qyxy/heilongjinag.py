#!/usr/bin/env python
#encoding=utf-8
import os
import requests
import time
import re
import random
import threading
import unittest
import settings
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import Parser
from crawler import CrawlerUtils
import types
import urlparse
import json

class HeilongjiangCrawler(Crawler):
    """江苏工商公示信息网页爬虫
    """
    #html数据的存储路径
    html_restore_path = settings.html_restore_path + '/heilongjiang/'

    #验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/heilongjiang/ckcode.jpg'

    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'www.hljaic.gov.cn',
            'official_site': 'http://gsxt.hljaic.gov.cn/search.jspx',
            'get_checkcode': 'http://gsxt.hljaic.gov.cn/validateCode.jspx?type=0',
            'post_checkcode': 'http://gsxt.hljaic.gov.cn/checkCheckNo.jspx',
            'post_checkcode2': 'http://gsxt.hljaic.gov.cn/searchList.jspx',
            'ind_comm_pub_skeleton': 'http://gsxt.hljaic.gov.cn/businessPublicity.jspx?',
            'ent_pub_skeleton': 'http://gsxt.hljaic.gov.cn/enterprisePublicity.jspx?',
            'other_dept_pub_skeleton': 'http://gsxt.hljaic.gov.cn/otherDepartment.jspx?',
            'judical_assist_skeleton': 'http://gsxt.hljaic.gov.cn/justiceAssistance.jspx?',
            # 'turn_page': 'http://gsxt.hljaic.gov.cn/QueryInvList.jspx?pno=2&mainId=D2F788D2201B4BA04DAF76DCA49473B3'
            }

    def __init__(self, json_restore_path):
        """
        初始化函数
        Args:
            json_restore_path: json文件的存储路径，所有江苏的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
             需要在写入文件的时候加锁
        Returns:
        """
        self.json_restore_path = json_restore_path

        # self.parser = HeilongjiangParser(self)
        self.reqst = requests.Session()
        self.reqst.headers.update({
                'Accept': 'text/html, application/xhtml+xml, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})
        self.corp_org = ''
        self.corp_id = ''
        self.corp_seq_id = ''
        self.common_enter_post_data = {}
        self.ci_enter_post_data = {}
        self.nb_enter_post_data = {}

        # self.json_restore_path = json_restore_path
        self.parser = HeilongjiangParser(self)

    def run(self, ent_number=0):
        self.ent_number = str(ent_number)
        #对每个企业都指定一个html的存储目录
        self.html_restore_path = self.html_restore_path + self.ent_number + '/'
        if settings.save_html and not os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)

        self.json_dict = {}

        result_ID = self.crawl_check_page()

        if result_ID == "Flase":
            settings.logger.error('crack check code failed, stop to crawl enterprise %s' % self.ent_number)
            return False

        self.crawl_ind_comm_pub_pages(result_ID)
        self.crawl_ent_pub_pages(result_ID)
        self.crawl_other_dept_pub_pages(result_ID)
        self.crawl_judical_assist_pub_pages(result_ID)
        # self.get_shareholder_info_details(result_ID)

        #采用多线程，在写入文件时需要注意加锁
        self.write_file_mutex.acquire()
        CrawlerUtils.json_dump_to_file(self.json_restore_path, {self.ent_number: self.json_dict})
        self.write_file_mutex.release()
        return True

    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        count = 0
        while count < 10:
            ckcode = self.crack_checkcode()
            data = {'checkNo': ckcode}
            resp = self.reqst.post(HeilongjiangCrawler.urls['post_checkcode'], data=data)

            if resp.status_code != 200:
                settings.logger.error("crawl post check page failed!")
                count += 1
                continue

            if resp.content.find("true") >= 0:
                ID = self.get_ID(ckcode)
                return ID
            else:
                settings.logger.error("crawl post check page failed!")
                count += 1
                continue
        return False

    def crack_checkcode(self):
        """破解验证码
        :return 破解后的验证码
        """
        resp = self.reqst.get(HeilongjiangCrawler.urls['official_site'])
        if resp.status_code != 200:
            return None

        resp = self.reqst.get(HeilongjiangCrawler.urls['get_checkcode'])
        if resp.status_code != 200:
            return None

        self.write_file_mutex.acquire()
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)
        ck_code = self.code_cracker.predict_result(self.ckcode_image_path)
        self.write_file_mutex.release()
        return ck_code[1]

    def get_ID(self, ckcode):
        """根据公司注册号，获得相对应的ID
        :return ID
        """
        data = {'checkNo': ckcode, 'entName': ent_number}
        resp = self.reqst.post(HeilongjiangCrawler.urls['post_checkcode2'], data=data)
        soup = BeautifulSoup(resp.text, "html5lib")
        div = soup.find("div", {"style": "height:500px;"})
        a = div.find("a")
        id = a["href"].split('?')[1]
        print id
        return id

    def crawl_page_by_url(self, url):
        """根据url直接爬取页面
        """
        resp = self.reqst.get(url)
        if self.reqst.status_code != 200:
            settings.logger.error('crawl page by url failed! url = %s' % url)
        page = resp.content
        time.sleep(random.uniform(0.2, 1))
        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.html_restore_path + 'detail.html', page)
        return page

    def crawl_ind_comm_pub_pages(self, result_ID):
        """爬取工商公示信息
        """
        url = "%s%s" % (HeilongjiangCrawler.urls['ind_comm_pub_skeleton'], result_ID)
        resp = self.reqst.get(url)
        self.parser.parse_ind_comm_pub_pages(resp.content)

        return resp.content

    def crawl_ent_pub_pages(self, result_ID):
        """爬取企业公示信息
        """
        url ="%s%s" % (HeilongjiangCrawler.urls['ent_pub_skeleton'], result_ID)
        resp = self.reqst.get(url)
        # print resp.content

    def crawl_other_dept_pub_pages(self, result_ID):
        """爬取其他部门公示信息
        """
        url = "%s%s" % (HeilongjiangCrawler.urls['other_dept_pub_skeleton'], result_ID)
        resp = self.reqst.get(url)
        # print resp.content

    def crawl_judical_assist_pub_pages(self, result_ID):
        """爬取司法协助信息
        """
        url = "%s%s" % (HeilongjiangCrawler.urls['judical_assist_skeleton'], result_ID)
        resp = self.reqst.get(url)
        # print resp.content

    # def get_shareholder_info_details(self, result_ID):
    #
    #     text = self.reqst.get("http://gsxt.hljaic.gov.cn/QueryInvList.jspx?pno=2&mainId=D2F788D2201B4BA04DAF76DCA49473B3")
    #     text = text.content
    #     ind_comm_pub_pages = self.crawl_ind_comm_pub_pages(result_ID)
    #     soup = BeautifulSoup(text)
    #     # div = soup.find("div", {"id": "invDiv"})
    #     links = soup.find_all("a")
    #     for a in links:
    #         re1 = '.*?'	# Non-greedy match on filler
    #         re2 = '\\d+'	# Uninteresting: int
    #         re3 = '.*?'	# Non-greedy match on filler
    #         re4 = '(\\d+)'	# Integer Number 1
    #
    #         rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
    #         m = rg.search(str(a))
    #         # m = rg.search(text)
    #         if m:
    #             int1 = m.group(1)
    #             print int1
    #
    # def turn_page(self, result_ID):
    #     url = HeilongjiangCrawler.urls['turn_page']+result_ID
    #     resp = self.reqst.get(url)
    #     print resp.content
    #
    #
    # def get_annual_report_detail(self, report_year, report_id):
    #     """获取企业年报的详细信息
    #     """
    #     annual_report_detail = {}
    #     post_data = self.nb_enter_post_data
    #     post_data['ID'] = report_id
    #     post_data['showRecordLine'] = '0'
    #     post_data['OPERATE_TYPE'] = '2'
    #     post_data['propertiesName'] = 'query_basicInfo'
    #     page_data = self.get_page_data('annual_report_detail', post_data)
    #     annual_report_detail[u'企业基本信息'] = self.parser.parse_page('annual_report_ent_basic_info', page_data)
    #     annual_report_detail[u'企业资产状况信息'] = self.parser.parse_page('annual_report_ent_property_info', page_data)
    #
    #     post_data['showRecordLine'] = '1'
    #     post_data['propertiesName'] = 'query_websiteInfo'
    #     page_data = self.get_page_data('annual_report_detail', post_data)
    #     annual_report_detail[u'网站或网店信息'] = self.parser.parse_page('annual_report_web_info', page_data)
    #
    #     post_data['propertiesName'] = 'query_investInfo'
    #     page_data = self.get_page_data('annual_report_detail', post_data)
    #     annual_report_detail[u'对外投资信息'] = self.parser.parse_page('annual_report_investment_abord_info', page_data)
    #
    #     post_data['MAIN_ID'] = report_id
    #     post_data['OPERATE_TYPE'] = '1'
    #     post_data['TYPE'] = 'NZGS'
    #     post_data['ADMIT_MAIN'] = '08'
    #     post_data['propertiesName'] = 'query_stockInfo'
    #     page_data = self.get_page_data('annual_report_detail', post_data)
    #     annual_report_detail[u'股东及出资信息'] = self.parser.parse_page('annual_report_shareholder_info', page_data)
    #
    #     post_data['propertiesName'] = 'query_InformationSecurity'
    #     page_data = self.get_page_data('annual_report_detail', post_data)
    #     annual_report_detail[u'对外提供保证担保信息'] = self.parser.parse_page('annual_report_external_guarantee_info', page_data)
    #
    #     post_data['propertiesName'] = 'query_RevisionRecord'
    #     page_data = self.get_page_data('annual_report_detail', post_data)
    #     annual_report_detail[u'修改记录'] = self.parser.parse_page('annual_report_modify_record', page_data)
    #     return annual_report_detail


class HeilongjiangParser(Parser):
    """北京工商页面的解析类
    """
    def __init__(self, crawler):
        self.crawler = crawler

    def parse_ind_comm_pub_pages(self, page):
        """解析工商公示信息-页面，在总局的页面中，工商公示信息所有信息都通过一个http get返回
        """
        soup = BeautifulSoup(page, "html5lib")

         # 一类表
        name_table_map = {
            u'基本信息': 'ind_comm_pub_reg_basic', # 登记信息-基本信息
            u'清算信息': 'ind_comm_pub_arch_liquidation', # 备案信息-清算信息
        }

        for table in soup.find_all('table'):
            list_table_title = table.find("th")
            if list_table_title is not None:
                if name_table_map.has_key(list_table_title.text):
                    table_name1 = name_table_map[list_table_title.text]
                    ths = table.find_all("th")
                    list_th = []
                    tds = table.find_all("td")
                    list_td = []
                    table3 = {}
                    for th in ths:
                        list_th.append(th.text)
                    for td in tds:
                        srting_tr = td.text
                        srt = srting_tr.strip()
                        if srt:
                            list_td.append(srt)
                        else:
                            list_td.append("None")
                    for i in range(1, len(list_th)):
                        table3[list_th[i]] = list_td[i-1]
                    # print table3
                    # self.crawler.json_dict[table_name1] = table3
        # 二类表
        id_table_map = {
            # 'touziren': 'ind_comm_pub_reg_shareholder',  # 股东信息
            'altDiv': 'ind_comm_pub_reg_modify',  # 登记信息-变更信息
            'memDiv': 'ind_comm_pub_arch_key_persons',  # 备案信息-主要人员信息
            "mortDiv": 'ind_comm_pub_movable_property_reg',  # 动产抵押登记信息
            "childDiv": 'ind_comm_pub_arch_branch',  # 备案信息-分支机构信息
            "pledgeDiv": 'ind_comm_pub_equity_ownership_reg',  # 股权出置登记信息
            "punDiv": 'ind_comm_pub_administration_sanction',  # 行政处罚信息
            "excDiv": 'ind_comm_pub_business_exception',  # 经营异常信息
            "serillDiv": 'ind_comm_pub_serious_violate_law',  # 严重违法信息
            "spotCheckDiv": 'ind_comm_pub_spot_check',  # 抽查检查信息
        }
        table_ids = id_table_map.keys()
        for table_id in table_ids:
            table_name = id_table_map[table_id]

            table1 = soup.find("div", {"id": table_id})

            # 获得表头
            previous_table = table1.previous_sibling.previous_sibling
            table_title1 = previous_table.find("tr")

            # 获得列名
            table_column = table_title1.next_sibling.next_sibling

            # 将列名存在列表里
            table_columns = [column for column in table_column.stripped_strings]

            # 获得列名列表长度
            len_colums = len(table_columns)

            # 获取内容表的每一列，并将每一列做成一个字典
            content_trs = table1.find_all("tr")
            if content_trs:
                table2 = []
                for content_tr in content_trs:
                    table_tr = {}
                    list_content_tr = [content for content in content_tr.stripped_strings]
                    for i in range(0, len_colums):
                        table_tr[table_columns[i]] = list_content_tr[i]
                    table2.append(table_tr)

                # 将表格信息存储到json中
                # print table2
                self.crawler.json_dict[table_name] = table2
            else:
                # print "表为空"
                self.crawler.json_dict[table_name] = []

    def get_detail_link(self, bs4_tag, page):
        """获取详情链接 url，在bs tag中或者page中提取详情页面
        Args:
            bs4_tag： beautifulsoup 的tag
            page: 页面数据
        """
        next_url = None
        if 'href' in bs4_tag.attrs.keys():
            next_url = bs4_tag['href']

        return next_url
if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    HeilongjiangCrawler.code_cracker = CaptchaRecognition('qinghai')
    crawler = HeilongjiangCrawler('./enterprise_crawler/heilongjiang.json')
    # enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/heilongjiang.txt')
    enterprise_list = ['230100100019556']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)
