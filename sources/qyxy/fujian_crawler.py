#!/usr/bin/env python
#encoding=utf-8
import os
import requests
import time
import re
import random
import threading
import unittest
from bs4 import BeautifulSoup
from crawler import Crawler
from crawler import Parser
from crawler import CrawlerUtils
from datetime import datetime, timedelta

ENT_CRAWLER_SETTINGS = os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings


class FujianCrawler(Crawler):
    """福建工商爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.html_restore_path + '/fujian/'

    # 验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/fujian/ckcode.jpg'

    # 多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'http://www.fjaic.gov.cn/',
            'official_site': 'http://wsgs.fjaic.gov.cn/creditpub/home',
            'get_checkcode': 'http://wsgs.fjaic.gov.cn/creditpub/captcha?preset=math-01',
            'post_checkcode': 'http://wsgs.fjaic.gov.cn/creditpub/security/verify_captcha',
            'get_info_entry': 'http://wsgs.fjaic.gov.cn/creditpub/search/ent_info_list',

            'open_info_entry': 'http://wsgs.fjaic.gov.cn/creditpub/notice/view?',  #获得企业信息页面的url，通过指定不同的tab=1-4来选择不同的内容（工商公示，企业公示...）
            'open_detail_info_entry': ''
        }

    def __init__(self, json_restore_path):
        self.json_restore_path = json_restore_path
        self.parser = FujianParser(self)
        self.img_count = 1

    def run(self, ent_number=0):
        """爬取的主函数
        """
        Crawler.run(self, ent_number)

    def crawl_check_page(self):
        """爬取验证码页面，包括获取验证码url，下载验证码图片，破解验证码并提交
        """
        count = 0
        next_url = self.urls['official_site']
        resp = self.reqst.get(next_url, verify=False)
        if resp.status_code != 200:
            settings.logger.error('failed to get official site')
            return False
        if not self.parse_pre_check_page(resp.content):
            settings.logger.error('failed to parse pre check page')
            return False

        while count < 30:
            # cur_time = datetime.now()
            # if cur_time >= settings.start_crawl_time + settings.max_crawl_time:
            #     settings.logger.info('crawl time over, exit!')
            #     return False

            count += 1
            ckcode = self.crack_checkcode()
            post_data = {'captcha': ckcode[1], 'session.token': self.session_token};
            next_url = self.urls['post_checkcode']
            resp = self.reqst.post(next_url, data=post_data, verify=False)
            if resp.status_code != 200:
                settings.logger.warn('failed to get crackcode image by url %s, fail count = %d' % (next_url, count))
                continue

            settings.logger.info('crack code = %s, %s, response =  %s' % (ckcode[0], ckcode[1], resp.content))
            if resp.content == '0':
                settings.logger.error('crack checkcode failed!')
                continue

            next_url = self.urls['get_info_entry']
            post_data = {
                'searchType': '1',
                'captcha': ckcode[1],
                'session.token': self.session_token,
                'condition.keyword': self.ent_number
             }
            resp = self.reqst.post(next_url, data=post_data, verify=False)
            if resp.status_code != 200:
                settings.logger.error('faild to crawl url %s' % next_url)
                return False

            if self.parse_post_check_page(resp.content):
                return True
            else:
                settings.logger.debug('crack checkcode failed, total fail count = %d' % count)
        return False

    def crawl_ind_comm_pub_pages(self):
        """爬取工商公示信息页面
        在福建的网站中，工商公示信息在一个页面中返回。页面中包含了多个表格，调用 Parser的 parse_ind_comm_page进行解析
        在 Parser的ind_comm_pub_page 中，访问并设置 crawler中的 json_dict。
        """
        next_url = self.urls['open_info_entry'] + 'uuid=' + self.uuid + '&tab=01'
        settings.logger.info('crawl ind comm pub pages, url:\n%s' % next_url)
        resp = self.reqst.get(next_url, verify=False)
        if resp.status_code != 200:
            settings.logger.warn('get ind comm pub info failed!')
            return False
        else:
            settings.logger.info('succcess to get ind comm pub info')
        self.parser.parse_ind_comm_pub_pages(resp.content)

    def crawl_ent_pub_pages(self):
        """爬取企业公示信息页面
        """
        next_url = self.urls['open_info_entry'] + 'uuid=' + self.uuid + '&tab=02'
        settings.logger.info('crawl ent pub pages, url:\n%s' % next_url)
        resp = self.reqst.get(next_url, verify=False)
        if resp.status_code != 200:
            settings.logger.warn('get ent pub info failed!')
            return False
        else:
            settings.logger.info('succcess to get ent pub info')
        self.parser.parse_ent_pub_pages(resp.content)

    def crawl_other_dept_pub_pages(self):
        """爬取其他部门公示信息页面
        """
        next_url = self.urls['open_info_entry'] + 'uuid=' + self.uuid + '&tab=03'
        settings.logger.info('crawl other dept pub pages, url:\n%s' % next_url)
        resp = self.reqst.get(next_url, verify=False)
        if resp.status_code != 200:
            settings.logger.warn('get other dept pub info failed!')
            return False
        else:
            settings.logger.info('succcess to get other pub info')
        self.parser.parse_other_dept_pub_pages(resp.content)

    def crawl_judical_assist_pub_pages(self):
        """爬取司法协助信息页面
        """
        next_url = self.urls['open_info_entry'] + 'uuid=' + self.uuid + '&tab=06'
        settings.logger.info('crawl judical assist pub pages, url:\n%s' % next_url)
        resp = self.reqst.get(next_url, verify=False)
        if resp.status_code != 200:
            settings.logger.warn('get judical assist info failed!')
            return False
        else:
            settings.logger.info('succcess to get judical assist info')
        self.parser.parse_judical_assist_pub_pages(resp.content)

    def parse_post_check_page(self, page):
        """解析提交验证码之后的页面，获取必要的信息
        """
        soup = BeautifulSoup(page)
        div_tag = soup.find('div', attrs={'class': 'link'})
        if not div_tag:
            return False
        open_info_url = div_tag.find('a').get('href')
        m = re.search(r'[/\w\.\?]+=([\w\.=]+)&.+', open_info_url)
        if m:
            self.uuid = m.group(1)
            return True
        else:
            return False

    def parse_pre_check_page(self, page):
        """解析提交验证码之前的页面
        """
        soup = BeautifulSoup(page, 'html.parser')
        input_tag = soup.find('input', attrs={'type': 'hidden', 'name': 'session.token'})
        if input_tag:
            self.session_token = input_tag.get('value')
            return True
        return False

    def crawl_page_by_url(self, url):
        """通过url直接获取页面
        """
        resp = self.reqst.get(url, verify=False)
        if resp.status_code != 200:
            settings.logger.error('failed to crawl page by url' % url)
            return
        page = resp.content
        time.sleep(random.uniform(0.2, 1))
        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.html_restore_path + 'detail.html', page)
        return page

    def crack_checkcode(self):
        """破解验证码"""
        checkcode_url = self.urls['get_checkcode'] + '&ra=' + str(random.random())

        resp = self.reqst.get(checkcode_url, verify=False)
        if resp.status_code != 200:
            settings.logger.warn('failed to get checkcode img')
            return
        page = resp.content

        time.sleep(random.uniform(2, 4))

        self.write_file_mutex.acquire()
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(page)
        if not self.code_cracker:
            print 'invalid code cracker'
            return ''
        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
        except Exception as e:
            settings.logger.warn('exception occured when crack checkcode')
            ckcode = ('', '')
            os.remove(self.ckcode_image_path)
            time.sleep(10)
        finally:
            pass
        self.write_file_mutex.release()
        return ckcode


class FujianParser(Parser):
    """北京工商页面的解析类
    """
    def __init__(self, crawler):
        self.crawler = crawler

    def parse_ind_comm_pub_pages(self, page):
        """解析工商公示信息-页面，在福建的页面中，工商公示信息所有信息都通过一个http get返回
        """
        soup = BeautifulSoup(page)
        id_table_map = {
            'branchTable': 'ind_comm_pub_arch_branch',      # 分支机构信息
            'punishTable': 'ind_comm_pub_administration_sanction',      # 行政处罚信息
            'spotcheckTable': 'ind_comm_pub_spot_check',        # 抽查检查信息
            # 'memberTable': 'ind_comm_pub_arch_key_persons',     # 备案信息-主要人员信息
            'pledgeTable': 'ind_comm_pub_equity_ownership_reg',     # 股权出质登记信息
            'mortageTable': 'ind_comm_pub_movable_property_reg',        # 动产抵押登记信息
            'exceptTable': 'ind_comm_pub_business_exception',       # 经营异常信息
            'investorTable': 'ind_comm_pub_reg_shareholder',        # 股东信息
            'alterTable': 'ind_comm_pub_reg_modify',        # 登记信息-变更信息
        }
        for table_id in id_table_map.keys():
            table = soup.find('table', attrs={'id': table_id})
            if table:
                table_name = id_table_map.get(table_id)
                settings.logger.info('crawler to get %s', table_name)
                self.crawler.json_dict[table_name] = self.parse_table(table, table_name, page)

        name_table_map = {
            u'基本信息': 'ind_comm_pub_reg_basic',
            u'清算信息': 'ind_comm_pub_arch_liquidation',
        }

        for table in soup.find_all('table'):
            table_title = self.get_table_title(table)
            table_name = name_table_map.get(table_title, None)
            if table_name:
                settings.logger.info('crawler to get %s', table_name)
                self.crawler.json_dict[table_name] = self.parse_table1(table)

        # 备案信息-主要人员信息
        table = soup.find("table", {"id": "memberTable"})
        if table:
            trs = table.find_all("tr")
            list_th = [th for th in trs[1].stripped_strings]
            table_save = []
            for tr in trs[2:]:
                content1 = {}
                content2 = {}
                list_td = []
                tds = tr.find_all("td")
                if not tds:
                    continue
                for td in tds:
                    list_td.append(td.text.strip())
                for i in range(0, 3):
                    content1[list_th[i]] = list_td[i]
                for i in range(3, 6):
                    content2[list_th[i]] = list_td[i]
                table_save.append(content1)
                table_save.append(content2)
            self.crawler.json_dict['ind_comm_pub_arch_key_persons'] = table_save
        else:
            self.crawler.json_dict['ind_comm_pub_arch_key_persons'] = []

    def parse_ent_pub_pages(self, page):
        """解析企业公示信息页面
        """
        soup = BeautifulSoup(page)
        name_table_map = {
            u'企业年报': 'ent_pub_ent_annual_report',
            u'行政许可信息': 'ent_pub_administration_license',
            u'知识产权出质登记信息': 'ent_pub_knowledge_property',
            u'股权变更信息': 'ent_pub_equity_change',
            u'变更信息': 'ent_pub_shareholder_modify'
        }
        for table in soup.find_all('table'):
            table_title = self.get_table_title(table)
            table_name = name_table_map.get(table_title, None)
            if table_name:
                settings.logger.info('crawler to get %s', table_name)
                self.crawler.json_dict[table_name] = self.parse_table(table, table_name, page)

    def parse_other_dept_pub_pages(self, page):
        """解析其他部门公示信息页面
        """
        soup = BeautifulSoup(page)
        name_table_map = {
            u'行政许可信息': 'other_dept_pub_administration_license',
            u'行政处罚信息': 'other_dept_pub_administration_sanction'
        }
        for table in soup.find_all('table'):
            table_title = self.get_table_title(table)
            table_name = name_table_map.get(table_title, None)
            if table_name:
                self.crawler.json_dict[table_name] = self.parse_table(table, table_name, page)

    def parse_judical_assist_pub_pages(self, page):
        """解析司法协助信息
        """
        soup = BeautifulSoup(page)
        name_table_map = {
            u'司法股权冻结信息': 'judical_assist_pub_equity_freeze'
        }
        for table in soup.find_all('table'):
            table_title = self.get_table_title(table)
            table_name = name_table_map.get(table_title, None)
            if table_name:
                self.crawler.json_dict[table_name] = self.parse_table(table, table_name, page)

    def parse_page(self, page, type):
        """解析页面
        返回 python 的字典形式数据
        """
        soup = BeautifulSoup(page, 'html.parser')
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:
                    # 一个页面中只含有一个表格
                    if len(soup.body.find_all('table')) == 1:
                        page_data = self.parse_table(soup.body.table, type, page)

                    # 页面中含有多个表格
                    else:
                        table = soup.body.find('table')
                        while table:
                            if table.name == 'table':
                                table_name = self.get_table_title(table)
                                page_data[table_name] = self.parse_table(table, table_name, page)
                            table = table.nextSibling
                except Exception as e:
                    settings.logger.error('parse failed, with exception %s' % e)
                    raise e

                finally:
                    pass
        return page_data

    def parse_list_table_without_sub_list(self, records_tag, table_name, page, columns):
        """提取没有子列的记录形式的表
        Args:
            records_tag: 表的记录标签，用beautiful soup 从html中提取出来的
            table_name: 表名
            page: 原始的html页面
            columns: 表的表头结构
        Returns:
            item_array: 提取出的表数据，列表形式，列表中的元素为一个python字典
        """
        item_array = []
        for tr in records_tag.find_all('tr'):
            col_count = 0
            item = {}
            for td in tr.find_all('td', recursive=False):
                if td.find('a'):
                    # try to retrieve detail link from page
                    next_url = self.get_detail_link(td.find('a'), page)
                    # has detail link
                    if next_url:
                        detail_page = self.crawler.crawl_page_by_url(next_url)
                        if table_name == 'ent_pub_ent_annual_report':
                            page_data = self.parse_ent_pub_annual_report_page(detail_page)
                            item[u'报送年度'] = CrawlerUtils.get_raw_text_in_bstag(td)
                            item[u'详情'] = page_data  # this may be a detail page data
                        elif table_name == 'ind_comm_pub_reg_shareholder':
                            page_data = self.parse_ind_comm_pub_shareholder_detail_page(detail_page)
                            item[u'详情'] = {"股东及出资信息": page_data}
                        else:
                            page_data = self.parse_page(detail_page, table_name + '_detail')
                            item[columns[col_count][0]] = page_data  # this may be a detail page data
                    else:
                        # item[columns[col_count]] = CrawlerUtils.get_raw_text_in_bstag(td)
                        item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                else:
                    item[columns[col_count][0]] = self.get_column_data(columns[col_count][1], td)
                col_count += 1
            if item:
                item_array.append(item)

        return item_array

    def parse_ind_comm_pub_shareholder_detail_page(self, page):
        """解析工商公示信息- 登记信息- 股东信息 中的详情链接页面
        """
        detail_dict = {}
        m = re.search(r'investor\.invName = \"(.+)\";', page)
        if m:
            detail_dict[u'股东'] = unicode(m.group(1), 'utf8')

        detail = {}
        m = re.search(r'invt\.subConAm = \"([\d\.]+)\";', page)
        if m:
            detail[u'认缴出资额（万元）'] = m.group(1)

        m = re.search(r'invt\.conDate = \'(.+)\';', page)
        if m:
            detail[u'认缴出资日期'] = m.group(1)
        m = re.search(r'invt\.conDate = \'([\w\-\.]*)\';', page)
        if m:
            detail[u'认缴出资日期'] = m.group(1)

        m = re.search(r'invt\.conForm = \"(.+)\";', page)
        if m:
            detail[u'认缴出资方式'] = m.group(1)

        # paid_in_detail = {}
        m = re.search(r'invtActl\.acConAm = \"([\d\.]+)\";', page)
        if m:
            detail[u'实缴出资额（万元）'] = m.group(1)

        m = re.search(r'invtActl\.conForm = \"(.+)\";', page)
        if m:
            detail[u'实缴出资方式'] = m.group(1)

        m = re.search(r'invtActl\.conDate = \'(.+)\';', page)
        if m:
            detail[u'实缴出资日期'] = m.group(1)
        m = re.search(r'invtActl\.conDate = \'([\w\-\.]*)\';', page)
        if m:
            detail[u'实缴出资日期'] = m.group(1)

        detail_dict[u'认缴额（万元）'] = detail.get(u'认缴出资额（万元）', '0')
        detail_dict[u'实缴额（万元）'] = detail.get(u'实缴出资额（万元）', '0')
        # detail_dict[u'认缴明细'] = subscribe_detail
        # detail_dict[u'实缴明细'] = paid_in_detail
        detail_dict[u"list"] = detail
        return detail_dict

    def parse_ent_pub_annual_report_page(self, page):
        """解析企业年报页面，该页面需要单独处理
        """
        soup = BeautifulSoup(page)
        table_names = (u'企业基本信息', u'网站或网店信息', u'股东及出资信息', u'对外投资信息',
                       u'企业资产状况信息', u'对外提供保证担保信息', u'股权变更信息', u'修改记录')
        annual_report_dict = {}
        for index, table in enumerate(soup.body.find_all('table')):
            table_name = table_names[index]
            annual_report_dict[table_name] = self.parse_table(table, table_name, page)

        return annual_report_dict

    def parse_table1(self, table):
        table_ths = table.find_all("th")
        table_th = []
        for th in table_ths:
            if 'colspan' in th.attrs:
                continue
            if th.text.strip() == "":
                continue
            table_th.append(th.text.strip())

        table_tds = table.find_all("td")
        table_td = [td.text.strip() for td in table_tds]

        table_save = {}
        for i in range(0, len(table_th)):
            table_save[table_th[i]] = table_td[i]
        return table_save

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
    FujianCrawler.code_cracker = CaptchaRecognition('fujian')

    crawler = FujianCrawler('./enterprise_crawler/fujian.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/fujian.txt')
    # enterprise_list = ['100000000018305']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('###############   Start to crawl enterprise with id %s   ################\n' % ent_number)
        crawler.run(ent_number=ent_number)