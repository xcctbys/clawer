#!/usr/bin/env python
# encoding=utf-8
import os
import requests
import time
import random
import threading
import unittest
import csv

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
        self.json_dict = {}

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

    def _save_results(self,content):
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
            time.sleep(0.1)
            self.crawl_year_report_json(data)
            time.sleep(0.1)
            self.crawl_year_report_detail_json(data)
            time.sleep(0.1)
            self.crawl_sfxzgdbg_json(data)
            time.sleep(0.1)
            self.crawl_sfxz_json(data)
            time.sleep(0.1)
            self.crawl_year_daily_invsub_json(data)
            time.sleep(0.1)
            self.crawl_year_daily_licinfo_json(data)
            time.sleep(0.1)
            self.crawl_year_daily_peninfo_json(data)
            time.sleep(0.1)
            self.crawl_year_daily_transinfo_json(data)
            time.sleep(0.1)
            self.crawl_year_daily_pleinfo_json(data)
            time.sleep(0.1)
            self.crawl_other_qpeninfo_json(data)
            time.sleep(0.1)
            self.crawl_other_qlicinfo_json(data)
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
                self.crawl_ent_info_json(data,type=10) # 有些公司需要传过去的参数为 10
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
    from CaptchaRecognition import CaptchaRecognition

    ChongqingClawer.code_cracker = CaptchaRecognition('chongqing')
    crawler = ChongqingClawer('./enterprise_crawler/chongqing.json')
    start_time = time.localtime()
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/chongqing.txt')
    for enterprise in enterprise_list:
        print('==================%s============\n' %str(enterprise))
        crawler.ent_number = str(enterprise)
        crawler.crawl_check_page()
        crawler.crawl_page_jsons()
        print('================================\n')
        time.sleep(1)

    # # print('==================%s============\n' %str(enterprise))
    # crawler.ent_number = str(500000400017721)
    # crawler.crawl_check_page()
    # crawler.crawl_page_jsons()
    # print('================================\n')
    # time.sleep(1)
    # crawler.ent_number = str(500000400046048)
    # crawler.crawl_check_page()
    # crawler.crawl_page_jsons()
    # print('================================\n')
    # time.sleep(1)
    # crawler.ent_number = str(500000000000311)
    # crawler.crawl_check_page()
    # crawler.crawl_page_jsons()
    # print('================================\n')
    # time.sleep(1)
    # crawler.ent_number = str(500000400003546)
    # crawler.crawl_check_page()
    # crawler.crawl_page_jsons()
    # print('================================\n')
    # time.sleep(1)
    # crawler.ent_number = '500000000002364'
    # crawler.crawl_check_page()
    # crawler.crawl_page_jsons()

    # i += 1
    # import run
    #
    # run.config_logging()
    # ChongqingClawer.code_cracker = CaptchaRecognition('chongqing')
    # crawler = ChongqingClawer('./enterprise_crawler/chongqing.json')
    # enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/chongqing.txt')
    # # enterprise_list = ['230100100019556']
    #
    # for ent_number in enterprise_list:
    #     ent_number = ent_number.rstrip('\n')
    #     settings.logger.info('############   Start to crawl enterprise with id %s   ################\n' % ent_number)
    #     crawler.run(ent_number=ent_number)
