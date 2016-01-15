#!/usr/bin/env python
# encoding=utf-8
import os
import requests
import time
import random
import threading
import unittest

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import Parser
from crawler import CrawlerUtils
import json as my_json


class ChongqingClawer(Crawler):
    """重庆工商公示信息网页爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.html_restore_path + '/chongqing/'

    # 验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/chongqing/ckcode.jpg'

    # 查询结果页面存储路径
    html_search_results_restore_path = html_restore_path + 'search_results.html'

    # 多线程爬取时往最后的json文件中写时的加锁保护
    urls = {
        'host': 'http://gsxt.cqgs.gov.cn',
        'get_checkcode': 'http://gsxt.cqgs.gov.cn/sc.action?width=130&height=40',
        'repost_checkcode': 'http://gsxt.cqgs.gov.cn/search_research.action',
        # 获得查询页面
        'post_checkcode': 'http://gsxt.cqgs.gov.cn/search.action',
        # 根据查询页面获得指定公司的数据
        'search_ent': 'http://gsxt.cqgs.gov.cn/search_getEnt.action',
        # 年报
        'year_report': 'http://gsxt.cqgs.gov.cn/search_getYearReport.action',
        # 年报详情
        'year_report_detail': 'http://gsxt.cqgs.gov.cn/search_getYearReportDetail.action',
        # 股权变更
        'year_daily_transinfo': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 股东出资信息
        'year_daily_invsub': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 行政处罚
        'year_daily_peninfo': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 行政许可
        'year_daily_licinfo': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 知识产权出质登记
        'year_daily_pleinfo': 'http://gsxt.cqgs.gov.cn/search_getDaily.action',
        # 其他行政许可信息
        'other_qlicinfo': 'http://gsxt.cqgs.gov.cn/search_getOtherSectors.action',
        # 其他行政处罚
        'other_qpeninfo': 'http://gsxt.cqgs.gov.cn/search_getOtherSectors.action',
        # 股权冻结信息
        'sfxz_page': 'http://gsxt.cqgs.gov.cn/search_getSFXZ.action',
        # 股东变更信息
        'sfxzgdbg_page': 'http://gsxt.cqgs.gov.cn/search_getSFXZGDBG.action',
    }
    write_file_mutex = threading.Lock()

    def __init__(self, json_restore_path):
        """
        初始化函数
        Args:
            json_restore_path: json文件的存储路径，所有重庆的企业，应该写入同一个文件，因此在多线程爬取时设置相同的路径。同时，
            需要在写入文件的时候加锁
        Returns:
        """
        # json 数据集
        # POST
        self.ent_number = None
        # GET
        self.ckcode = None
        self.json_ent_info = None
        self.json_sfxzgdbg = None
        self.json_sfxz = None
        self.json_other_qlicinfo = None
        self.json_other_qpeninfo = None
        self.json_year_report = None
        self.json_year_report_detail = None
        self.json_year_daily_transinfo = None
        self.json_year_daily_invsub = None
        self.json_year_daily_peninfo = None
        self.json_year_daily_licinfo = None
        self.json_year_daily_pleinfo = None

        self.json_restore_path = json_restore_path
        self.parser = ChongqingParser(self)
        self.reqst = requests.Session()
        self.reqst.headers.update({
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

    def run(self, ent_number=0):
        self.ent_number = str(ent_number)
        # 对每个企业都指定一个html的存储目录
        self.html_restore_path = self.html_restore_path + self.ent_number + '/'
        if settings.save_html and not os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)
        crawler.ent_number = str(ent_number)
        crawler.crawl_check_page()
        crawler.crawl_page_jsons()
        crawler.parser.parse_jsons()
        crawler.parser.merge_jsons(crawler.json_restore_path)

    def crawl_check_page(self):
        """爬取验证码页面，包括下载验证码图片以及破解验证码
        :return true or false
        """
        # 获得验证码图片
        while self.ckcode is None:
            if self._get_checkcode(ChongqingClawer.urls['get_checkcode']) is True:
                self.ckcode = self.crack_checkcode()

        data = {'code': self.ckcode, 'key': self.ent_number}
        content = self._get_search_page(data)
        # print(content)
        check_string = '验证码不正确'
        if check_string in str(content):
            print(str(content) + 'null')
            self.ckcode = None
            self.crawl_check_page()

        else:
            self._save_results(content)

    def _get_search_page(self, data):
        resp = self.reqst.post(ChongqingClawer.urls['post_checkcode'], data)
        if resp.status_code == 200:
            pass
        else:
            while True:
                data.append({'stype': ""})
                resp = self.reqst.post(ChongqingClawer.urls['repost_checkcode', data])
                if resp.status_code == 200:
                    break
        return resp.content

    def _save_results(self, content):
        self.write_file_mutex.acquire()
        try:
            with open(self.html_search_results_restore_path, 'wb') as f:
                f.write(content)
                f.close()
        except Exception as e:
            settings.logger.error('write results page file wrong ')
        self.write_file_mutex.release()

    def _get_checkcode(self, url):
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            resp = self.reqst.get(url)
        self.write_file_mutex.acquire()
        try:
            with open(self.ckcode_image_path, 'wb') as f:
                f.write(resp.content)
                f.close()
        except Exception as e:
            settings.logger.error('write down file wrong ')
            return False
        self.write_file_mutex.release()
        return True

    def crack_checkcode(self):
        """破解验证码
        :return 破解后的验证码
        """
        resp = self.reqst.get(ChongqingClawer.urls['get_checkcode'])
        if resp.status_code != 200:
            settings.logger.error('failed to get get_checkcode')
            print 'error'
            return None

        time.sleep(random.uniform(2, 4))

        self.write_file_mutex.acquire()
        self.ckcode_image_path = settings.json_restore_path + '/chongqing/ckcode.jpg'
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)
        self.write_file_mutex.release()

        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
            print("try:", str(ckcode), self.ckcode_image_path)
        except Exception as e:
            settings.logger.warn('exception occured when crack checkcode')
            ckcode = ('', '')
            print("except", str(ckcode), self.ckcode_image_path)
        finally:
            pass

        return ckcode[1]

    def crawl_page_jsons(self):
        """获取所有界面的json数据"""
        data = self.parser.parse_search_results_pages(self.html_search_results_restore_path)
        if data is not None:
            self.crawl_ent_info_json(data)
            print(self.json_ent_info)
            # time.sleep(0.1)
            self.crawl_year_report_json(data)
            print(self.json_year_report)
            # time.sleep(0.1)
            self.crawl_year_report_detail_json(data)
            print(self.json_year_report_detail)
            # time.sleep(0.1)
            self.crawl_sfxzgdbg_json(data)
            print(self.json_sfxzgdbg)
            # time.sleep(0.1)
            self.crawl_sfxz_json(data)
            print(self.json_sfxz)
            # time.sleep(0.1)
            self.crawl_year_daily_invsub_json(data)
            print(self.json_year_daily_invsub)
            # time.sleep(0.1)
            self.crawl_year_daily_licinfo_json(data)
            print(self.json_year_daily_licinfo)
            # time.sleep(0.1)
            self.crawl_year_daily_peninfo_json(data)
            print(self.json_year_daily_peninfo)
            # time.sleep(0.1)
            self.crawl_year_daily_transinfo_json(data)
            print(self.json_year_daily_transinfo)
            # time.sleep(0.1)
            self.crawl_year_daily_pleinfo_json(data)
            print(self.json_year_daily_pleinfo)
            # time.sleep(0.1)
            self.crawl_other_qpeninfo_json(data)
            print(self.json_other_qpeninfo)
            # time.sleep(0.1)
            self.crawl_other_qlicinfo_json(data)
            print(self.json_other_qlicinfo)
        else:
            print('error')

    def crawl_ent_info_json(self, data, type=1):
        """企业详细信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'type': type}
        json = self.reqst.get(ChongqingClawer.urls['search_ent'], params=params)
        if json.status_code == 200:
            json = json.content
            json = str(json)
            self.json_ent_info = json[6:]  # 去掉数据中的前六个字符保证数据为完整json格式数据
            if self.json_ent_info is None or 'base' not in self.json_ent_info:
                self.crawl_ent_info_json(data, type=10)  # 有些公司需要传过去的参数为 10
                # print(self.json_ent_info)

    def crawl_year_report_json(self, data):
        """年报数据"""
        params = {'id': data.get('id'), 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['year_report'], params=params)
        while json.status_code != 200:
            json = self.reqst.get(ChongqingClawer.urls['year_report'], params=params)
        json = json.content
        json = str(json)
        self.json_year_report = json[6:]  # 去掉数据中的前六个字符保证数据为完整json格式数据
        # print(self.json_year_report)

    def crawl_year_report_detail_json(self, data):
        """详细年报"""
        # TO DO 需要获得 year_report 中的年份信息
        while self.json_year_report is None:
            self.crawl_year_report_json(data)
        year_report = my_json.loads(self.json_year_report, encoding='utf-8')
        histories = year_report.get('history')
        for i in range(len(histories)):
            year = histories[i].get('year')
            params = {'id': data.get('id'), 'type': 1, 'year': str(year)}
            json = self.reqst.get(ChongqingClawer.urls['year_report_detail'], params=params)
            if json.status_code == 200:
                # 此页面响应结果直接就是 json
                self.json_year_report_detail = str(json.content)
                # print(self.json_year_report_detail)

    def crawl_year_daily_transinfo_json(self, data):
        """股权变更"""
        params = {'id': data.get('id'), 'jtype': 'transinfo'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_transinfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_transinfo = json[6:]
            # print(self.json_year_daily_transinfo)

    def crawl_year_daily_pleinfo_json(self, data):
        """行政许可"""
        params = {'id': data.get('id'), 'jtype': 'pleinfo'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_pleinfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_pleinfo = json[6:]
            # print(self.json_year_daily_pleinfo)

    def crawl_year_daily_invsub_json(self, data):
        """股东出资信息"""
        params = {'id': data.get('id'), 'jtype': 'invsub'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_invsub'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_invsub = json[6:]
            # print(self.json_year_daily_invsub)

    def crawl_year_daily_licinfo_json(self, data):
        """行政许可"""
        params = {'id': data.get('id'), 'jtype': 'licinfo'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_licinfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_licinfo = json[6:]
            # print(self.json_year_daily_licinfo)

    def crawl_year_daily_peninfo_json(self, data):
        """行政处罚"""
        params = {'id': data.get('id'), 'jtype': 'peninfo'}
        json = self.reqst.get(ChongqingClawer.urls['year_daily_peninfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_year_daily_peninfo = json[6:]
            # print(self.json_year_daily_peninfo)

    def crawl_sfxzgdbg_json(self, data):
        """股东变更信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['sfxzgdbg_page'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_sfxzgdbg = json[6:]
            # print(self.json_sfxzgdbg)

    def crawl_sfxz_json(self, data):
        """股权冻结信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['sfxz_page'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_sfxz = json[6:]
            # print(self.json_sfxz)

    def crawl_other_qlicinfo_json(self, data):
        """股东出资信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'qtype': 'Qlicinfo', 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['other_qlicinfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_other_qlicinfo = json[6:]
            # print(self.json_other_qlicinfo)

    def crawl_other_qpeninfo_json(self, data):
        """股东出资信息"""
        params = {'entId': data.get('entId'), 'id': data.get('id'), 'qtype': 'Qpeninfo', 'type': 1}
        json = self.reqst.get(ChongqingClawer.urls['other_qpeninfo'], params=params)
        if json.status_code == 200:
            # 此页面响应结果直接就是 json
            json = json.content
            json = str(json)
            self.json_other_qpeninfo = json[6:]
            # print(self.json_other_qpeninfo)


class ChongqingParser(Parser):
    """重庆工商页面的解析类
    """

    def __init__(self, crawler):
        self.crawler = crawler
        self.json_dict = {}
        self.ind_comm_pub_reg_basic = {}
        self.ind_comm_pub_reg_shareholder = None
        self.ind_comm_pub_reg_modify = None
        self.ind_comm_pub_arch_key_persons = None
        self.ind_comm_pub_arch_branch = None
        self.ind_comm_pub_arch_liquidation = None
        self.ind_comm_pub_movable_property_reg = None
        self.ind_comm_pub_equity_ownership_reg = None
        self.ind_comm_pub_administration_sanction = None
        self.ind_comm_pub_business_exception = None
        self.ind_comm_pub_serious_violate_law = None
        self.ind_comm_pub_spot_check = None
        self.ent_pub_shareholder_capital_contribution = None
        self.ent_pub_equity_change = None
        self.ent_pub_administration_license = None
        self.ent_pub_knowledge_property = None
        self.ent_pub_administration_sanction = None
        self.other_dept_pub_administration_license = None
        self.other_dept_pub_administration_sanction = None
        self.judical_assist_pub_equity_freeze = None
        self.judical_assist_pub_shareholder_modify = None

    def parse_search_results_pages(self, page):
        # 解析供查询页面, 获得工商信息页面POST值
        page_content = open(page)
        content = page_content.read()
        soup = BeautifulSoup(content, "html5lib")
        result = soup.find('div', {'id': 'result'})
        key_map = {}
        item = result.find('div', {'class': 'item'})
        link = item.find('a')
        entId = link.get('data-entid')
        type = link.get('data-type')
        id = link.get('data-id')
        name = link.get_text()
        key_map['entId'] = entId
        key_map['type'] = type
        key_map['id'] = id
        key_map['name'] = name
        if key_map is not None:
            return key_map
        else:
            return None

    def parse_jsons(self):
        self.parse_json_ent_info()
        self.parse_json_year_report()
        self.parse_json_sfxzgdbg()
        self.parse_json_sfxz()
        self.parse_json_year_daily_peninfo()
        self.parse_json_year_daily_licinfo()
        self.parse_json_year_daily_invsub()
        self.parse_json_year_daily_pleinfo()
        self.parse_json_year_daily_transinfo()
        self.parse_json_year_report_detail()
        self.parse_json_other_qpeninfo()
        self.parse_json_other_qlicinfo()

    def merge_jsons(self,json_restore_path):
        all_date = {}
        all_date['ind_comm_pub_reg_basic'] = self.ind_comm_pub_reg_basic
        all_date['ind_comm_pub_reg_shareholder'] = self.ind_comm_pub_reg_shareholder
        all_date['ind_comm_pub_reg_modify'] = self.ind_comm_pub_reg_modify
        all_date['ind_comm_pub_arch_key_persons'] = self.ind_comm_pub_arch_key_persons
        all_date['ind_comm_pub_arch_branch'] = self.ind_comm_pub_arch_branch
        all_date['ind_comm_pub_arch_liquidation'] = self.ind_comm_pub_arch_liquidation
        all_date['ind_comm_pub_movable_property_reg'] = self.ind_comm_pub_movable_property_reg
        all_date['ind_comm_pub_equity_ownership_reg'] = self.ind_comm_pub_equity_ownership_reg
        all_date['ind_comm_pub_administration_sanction'] = self.ind_comm_pub_administration_sanction
        all_date['ind_comm_pub_business_exception'] = self.ind_comm_pub_business_exception
        all_date['ind_comm_pub_serious_violate_law'] = self.ind_comm_pub_serious_violate_law
        all_date['ind_comm_pub_spot_check'] = self.ind_comm_pub_spot_check
        all_date['ent_pub_shareholder_capital_contribution'] = self.ent_pub_shareholder_capital_contribution
        all_date['ent_pub_equity_change'] = self.ent_pub_equity_change
        all_date['ent_pub_administration_license'] = self.ent_pub_administration_license
        all_date['ent_pub_knowledge_property'] = self.ent_pub_knowledge_property
        all_date['ent_pub_administration_sanction'] = self.ent_pub_administration_sanction
        all_date['other_dept_pub_administration_license'] = self.other_dept_pub_administration_license
        all_date['other_dept_pub_administration_sanction'] = self.other_dept_pub_administration_sanction
        all_date['judical_assist_pub_equity_freeze'] = self.judical_assist_pub_equity_freeze
        all_date['judical_assist_pub_shareholder_modify'] = self.judical_assist_pub_shareholder_modify
        jsones = {}
        jsones[str(self.crawler.ent_number)] = all_date
        my_json.dump(jsones, open(json_restore_path, 'a'))
        with open(json_restore_path, 'a') as json_file:
            json_file.write('\n')

        pass
    def check_key_is_exists(self, investor, sharehodler, newkey, oldkey):
        if oldkey in investor.keys():
            sharehodler[newkey] = str(investor[oldkey]).strip(' ')
        else:
            sharehodler[newkey] = None

    def parse_json_ent_info(self):
        print self.crawler.json_ent_info
        json_ent_info = my_json.loads(self.crawler.json_ent_info)
        # 公司基本信息
        base_info = json_ent_info.get('base')
        print json_ent_info.keys()
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'register_capital', 'regcap')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'business_scope', 'opscope')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'credit_code', 'pripid')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'time_end', 'opto')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'register_num', 'estdate')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'place', 'dom')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'enter_name', 'entname')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'check_date', 'apprdate')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'enter_type', 'enttype')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'register_status', 'opstate')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'corporation', 'lerep')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'register_gov', 'regorg')
        self.check_key_is_exists(base_info, self.ind_comm_pub_reg_basic, 'time_start', 'opfrom')
        print(self.ind_comm_pub_reg_basic)

        # 股东基本信息
        investors = json_ent_info.get('investors')
        sharehodlers = []
        print(investors)
        i = 0
        while i < len(investors):
            sharehodler = {}
            print(investors[i])
            self.check_key_is_exists(investors[i], sharehodler, 'shareholder_type', 'invtype')
            self.check_key_is_exists(investors[i], sharehodler, 'certificate_number', 'oid')
            if len(investors[i].get('gInvaccon')) > 0:
                self.check_key_is_exists(investors[i].get('gInvaccon')[0], sharehodler, 'subscription_date', 'accondate')
                self.check_key_is_exists(investors[i], sharehodler, 'subscription_amount', 'lisubconam')
                self.check_key_is_exists(investors[i].get('gInvaccon')[0], sharehodler, 'subscription_type', 'acconform')
                self.check_key_is_exists(investors[i].get('gInvaccon')[0], sharehodler, 'subscription_money_amount', 'acconam')
            self.check_key_is_exists(investors[i], sharehodler, 'paid_amount', 'liacconam')
            if len(investors[i].get('gInvsubcon')) > 0:
                self.check_key_is_exists(investors[i].get('gInvsubcon')[0], sharehodler, 'paid_type', 'conform')
                self.check_key_is_exists(investors[i].get('gInvsubcon')[0], sharehodler, 'paid_date', 'condate')
                self.check_key_is_exists(investors[i].get('gInvsubcon')[0], sharehodler, 'paid_money_amount', 'subconam')
            self.check_key_is_exists(investors[i], sharehodler, 'shareholder_name', 'inv')
            self.check_key_is_exists(investors[i], sharehodler, 'certificate_type', 'blictype')
            sharehodlers.append(sharehodler)
            i = i + 1
        # for share in sharehodlers:
        #     print(share)
        self.ind_comm_pub_reg_shareholder = sharehodlers
        print ('===================================')

        # 变更信息
        modifies = []
        modify = {}
        alters = json_ent_info.get('alters')
        for alter in alters:
            self.check_key_is_exists(alter, modify, 'modify_item', 'altitem')
            self.check_key_is_exists(alter, modify, 'modify_date', 'altdate')
            self.check_key_is_exists(alter, modify, 'modify_after', 'altaf')
            self.check_key_is_exists(alter, modify, 'modify_before', 'altbe')
            modifies.append(modify)
        self.ind_comm_pub_reg_modify = modifies
        for item in modifies:
            print item

        # 主要人物
        key_persons = []
        members = json_ent_info.get('members')
        i = 0
        while i < len(members):
            print(members[i])
            key_person = {}
            key_person['enter_id'] = i + 1
            self.check_key_is_exists(members[i], key_person, 'name', 'name')
            self.check_key_is_exists(members[i], key_person, 'position', 'position')
            key_persons.append(key_person)
            i += 1
        self.ind_comm_pub_arch_key_persons = key_persons
        print key_persons

        # 动产抵押
        movable_property_reges = []
        motages = json_ent_info.get('motage')
        i = 0
        while i < len(motages):
            print(motages[i])
            movable_property_reg = {}
            movable_property_reg['enter_id'] = i + 1
            self.check_key_is_exists(motages[i], movable_property_reg, 'status', '')
            self.check_key_is_exists(motages[i], movable_property_reg, 'sharechange_register_date', 'regidate')
            self.check_key_is_exists(motages[i], movable_property_reg, 'register_num', 'morregcno')
            self.check_key_is_exists(motages[i], movable_property_reg, 'guarantee_debt_amount', 'priclasecam')
            self.check_key_is_exists(motages[i], movable_property_reg, 'register_gov', 'regorg')
            movable_property_reges.append(movable_property_reg)
            i += 1
        self.ind_comm_pub_movable_property_reg = movable_property_reges
        print(movable_property_reges)

        # 行政处罚
        administration_sanctions = []
        punishments = json_ent_info.get('punishments')
        i = 0
        while i < len(punishments):
            print(punishments[i])
            administration_sanction = {}
            administration_sanction['enter_id'] = i + 1
            self.check_key_is_exists(punishments[i], administration_sanction, 'penalty_content', 'authcontent')
            self.check_key_is_exists(punishments[i], administration_sanction, 'penalty_decision_gov', 'penauth')
            self.check_key_is_exists(punishments[i], administration_sanction, 'illegal_type', 'illegacttype')
            self.check_key_is_exists(punishments[i], administration_sanction, 'penalty_decision_date', 'pendecissdate')
            self.check_key_is_exists(punishments[i], administration_sanction, 'penalty_decision_num', 'pendecno')
            administration_sanctions.append(administration_sanction)
            i += 1
        self.ind_comm_pub_administration_sanction = administration_sanctions
        print(administration_sanctions)

        # 分支机构
        arch_branches = []
        brunchs = json_ent_info.get('brunchs')
        i = 0
        while i < len(brunchs):
            print(brunchs[i])
            arch_branch = {}
            arch_branch['enter_id'] = i + 1
            self.check_key_is_exists(brunchs[i], arch_branch, 'register_gov', 'regorgname')
            self.check_key_is_exists(brunchs[i], arch_branch, 'enter_code', 'regno')
            self.check_key_is_exists(brunchs[i], arch_branch, 'branch_name', 'brname')
            arch_branches.append(arch_branch)
            i += 1
        self.ind_comm_pub_arch_branch = arch_branches
        print(arch_branches)

        # 严重违法
        serious_violate_laws = []
        illegals = json_ent_info.get('illegals')
        i = 0
        while i < len(illegals):
            # print(illegals[i])
            serious_violate_law = {}
            serious_violate_law['enter_id'] = i + 1
            self.check_key_is_exists(illegals[i], serious_violate_law, 'list_out_reason', 'remexcpres')
            self.check_key_is_exists(illegals[i], serious_violate_law, 'list_on_reason', 'serillrea')
            self.check_key_is_exists(illegals[i], serious_violate_law, 'decision_gov', 'decorg')
            self.check_key_is_exists(illegals[i], serious_violate_law, 'list_on_date', 'lisdate')
            self.check_key_is_exists(illegals[i], serious_violate_law, 'list_out_date', 'remdate')
            serious_violate_laws.append(serious_violate_law)
            i += 1
        self.ind_comm_pub_serious_violate_law = serious_violate_laws
        print(serious_violate_laws)

        # 抽查检查
        spot_checkes = []
        ccjces = json_ent_info.get('ccjc')
        i = 0
        while i < len(ccjces):
            print(ccjces[i])
            spot_check = {}
            spot_check['enter_id'] = i + 1
            self.check_key_is_exists(ccjces[i], spot_check, 'check_gov', 'insauth')
            self.check_key_is_exists(ccjces[i], spot_check, 'check_result', 'insresname')
            self.check_key_is_exists(ccjces[i], spot_check, 'check_type', 'instype')
            self.check_key_is_exists(ccjces[i], spot_check, 'check_date', 'insdate')
            spot_checkes.append(spot_check)
            i += 1
        self.ind_comm_pub_spot_check = spot_checkes
        print(spot_checkes)

        # 经营异常
        business_exceptiones = []
        qyjyes = json_ent_info.get('qyjy')
        i = 0
        while i < len(qyjyes):
            # print(qyjyes[i])
            business_exception = {}
            business_exception['enter_id'] = i + 1
            self.check_key_is_exists(qyjyes[i], business_exception, 'list_out_reason', 'remexcpres')
            self.check_key_is_exists(qyjyes[i], business_exception, 'list_gov', 'decorg')
            self.check_key_is_exists(qyjyes[i], business_exception, 'list_on_reason', 'specause')
            self.check_key_is_exists(qyjyes[i], business_exception, 'list_on_date', 'abntime')
            self.check_key_is_exists(qyjyes[i], business_exception, 'list_out_date', 'remdate')
            business_exceptiones.append(business_exception)
            i += 1
        self.ind_comm_pub_business_exception = business_exceptiones
        # print '经营异常=', business_exceptiones

        # 清算
        arch_liquidationes = []
        accounts = json_ent_info.get('accounts')
        i = 0
        while i < len(accounts):
            # print accounts[i]
            arch_liquidation = {}
            arch_liquidation['enter_id'] = i + 1
            self.check_key_is_exists(accounts[i], arch_liquidation, 'persons', 'persons')
            self.check_key_is_exists(accounts[i], arch_liquidation, 'person_in_change', 'ligprincipal')
            business_exceptiones.append(arch_liquidation)
            i += 1
        self.ind_comm_pub_arch_liquidation = arch_liquidationes
        # print '清算==', arch_liquidationes

        # 股权出质
        equity_ownership_reges = []
        stockes = json_ent_info.get('stock')
        i = 0
        while i < len(stockes):
            print stockes[i]
            equity_ownership_reg = {}
            equity_ownership_reg['enter_id'] = i + 1
            self.check_key_is_exists(stockes[i], equity_ownership_reg, 'share_pledge_num', 'pripid')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, 'publicity_time', 'equpledate')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, 'status', 'type')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, 'mortgagee', 'imporg')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, 'pledgor', 'pledgor')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, 'register_num', 'equityno')
            self.check_key_is_exists(stockes[i], equity_ownership_reg, 'pledgor_certificate_code', 'impno')
            equity_ownership_reges.append(equity_ownership_reg)
            i += 1
        self.ind_comm_pub_equity_ownership_reg = equity_ownership_reges
        # print '股权出质', equity_ownership_reges

    def parse_json_year_report(self):
        pass

    def parse_json_sfxzgdbg(self):
        print self.crawler.json_sfxzgdbg
        json_sfxzgdbg = my_json.loads(self.crawler.json_sfxzgdbg)
        shareholder_modifies = []
        self.judical_assist_pub_shareholder_modify = shareholder_modifies
        # ========================
        # 暂时没有数据
        # 正式时需要添加序号
        # ========================
        # self.check_key_is_exists(,,'been_excute_name','inv')
        # self.check_key_is_exists(,,'share_num','froam')
        # self.check_key_is_exists(,,'excute_court','froauth')
        # self.check_key_is_exists(,,'assignee','alien')
        # =====================================================
        # print shareholder_modifies

    def parse_json_sfxz(self):
        print self.crawler.json_sfxz
        json_sfxz = my_json.loads(self.crawler.json_sfxz)
        equity_freezes = []
        i = 0
        while i < len(json_sfxz):
            equity_freez = {}
            equity_freez['enter_id'] = i + 1
            self.check_key_is_exists(json_sfxz[i], equity_freez, 'freeze_status', 'frozstate')
            self.check_key_is_exists(json_sfxz[i], equity_freez, 'been_excute_person', 'inv')
            self.check_key_is_exists(json_sfxz[i], equity_freez, 'share_num', 'froam')
            self.check_key_is_exists(json_sfxz[i], equity_freez, 'excute_court', 'froauth')
            self.check_key_is_exists(json_sfxz[i], equity_freez, 'notice_num', 'executeno')
            i += 1
        self.judical_assist_pub_equity_freeze = equity_freezes
        # print ' 股权冻结', equity_freezes

    def parse_json_year_daily_peninfo(self):
        pass

    def parse_json_year_daily_licinfo(self):
        pass

    def parse_json_year_daily_invsub(self):
        pass

    def parse_json_year_daily_pleinfo(self):
        pass

    def parse_json_year_daily_transinfo(self):
        pass

    def parse_json_year_report_detail(self):
        pass

    def parse_json_other_qpeninfo(self):
        print self.crawler.json_other_qpeninfo
        json_other_qpeninfo = my_json.loads(self.crawler.json_other_qpeninfo)

    def parse_json_other_qlicinfo(self):
        print self.crawler.json_other_qlicinfo
        json_other_qlicinfoes = my_json.loads(self.crawler.json_other_qlicinfo)
        administration_licenses = []
        i = 0
        while i < len(json_other_qlicinfoes):
            administration_license = {}
            administration_license['enter_id'] = i + 1
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, 'license_status', 'type')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, 'license_end_date', 'valto')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, 'license_content', 'licitem')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, 'license_filename', 'licname')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, 'license_file_num', 'licno')
            # 暂时没有确定
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, 'license_detail',
                                     'license_detail')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, 'license_authority_gov',
                                     'licanth')
            self.check_key_is_exists(json_other_qlicinfoes[i], administration_license, 'license_begin_date', 'valfrom')
            administration_licenses.append(administration_license)
            i += 1
        self.other_dept_pub_administration_license = administration_licenses
        # print '行政许可===', administration_licenses


class TestParser(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        from CaptchaRecognition import CaptchaRecognition
        self.crawler = ChongqingClawer('./enterprise_crawler/chongqing.json')
        self.parser = self.crawler.parser
        ChongqingClawer.code_cracker = CaptchaRecognition('chongqing')
        self.crawler.json_dict = {}
        self.crawler.ent_number = '500232000003942'


if __name__ == '__main__':

    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")
    from CaptchaRecognition import CaptchaRecognition

    ChongqingClawer.code_cracker = CaptchaRecognition('chongqing')
    crawler = ChongqingClawer('./enterprise_crawler/chongqing.json')
    start_time = time.localtime()
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/chongqing.txt')
    for enterprise in enterprise_list:
        print('==================%s============\n' % str(enterprise))
        crawler.run(enterprise)

