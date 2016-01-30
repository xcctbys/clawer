 #!/usr/bin/env python
# encoding=utf-8
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
import types
import urlparse
import json
ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings


class QinghaiCrawler(Crawler):
    """青海工商公示信息网页爬虫
    """
    # html数据的存储路径
    html_restore_path = settings.html_restore_path + '/qinghai/'

    # 验证码图片的存储路径
    ckcode_image_path = settings.json_restore_path + '/qinghai/ckcode.jpg'

    # 多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    urls = {'host': 'www.hljaic.gov.cn',
            'get_checkcode': 'http://218.95.241.36/validateCode.jspx?type=0',
            'post_checkCode': 'http://218.95.241.36/checkCheckNo.jspx',
            'post_checkCode2': 'http://218.95.241.36/searchList.jspx',
            'ind_comm_pub_skeleton': 'http://218.95.241.36/businessPublicity.jspx?',
            'ent_pub_skeleton': 'http://218.95.241.36/enterprisePublicity.jspx?',
            'other_dept_pub_skeleton': 'http://218.95.241.36/otherDepartment.jspx?',
            'judical_assist_skeleton': 'http://218.95.241.36/justiceAssistance.jspx?',

            'ind_comm_pub_reg_shareholder': 'http://218.95.241.36/QueryInvList.jspx?',# 股东信息
            'ind_comm_pub_reg_modify': 'http://218.95.241.36/QueryAltList.jspx?',  # 变更信息翻页
            'ind_comm_pub_arch_key_persons': 'http://218.95.241.36/QueryMemList.jspx?',  # 主要人员信息翻页
            'ind_comm_pub_spot_check': 'http://218.95.241.36/QuerySpotCheckList.jspx?',  # 抽样检查信息翻页
            'ind_comm_pub_movable_property_reg': 'http://218.95.241.36/QueryMortList.jspx?',  # 动产抵押登记信息翻页
            'ind_comm_pub_business_exception': 'http://218.95.241.36/QueryExcList.jspx?',  # 经营异常信息

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
        self.parser = QinghaiParser(self)

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
        self.company_id = ''

    def run(self, ent_number=0):
        self.ent_number = str(ent_number)
        # 对每个企业都指定一个html的存储目录
        self.html_restore_path = self.html_restore_path + self.ent_number + '/'
        if settings.save_html and not os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)

        self.json_dict = {}

        result_ID = self.crawl_check_page()

        if result_ID == "Flase":
            settings.logger.error('crack check code failed, stop to crawl enterprise %s' % self.ent_number)
            return False
        if result_ID == "None":
            settings.logger.error('According to the registration number does not search to the company %s' % self.ent_number)
            return False

        self.crawl_ind_comm_pub_pages()
        self.crawl_ent_pub_pages()
        self.crawl_other_dept_pub_pages()
        self.crawl_judical_assist_pub_pages()

        # 采用多线程，在写入文件时需要注意加锁
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
            ck_code = self.crack_check_code()

            data = {'checkNo': ck_code}
            resp = self.reqst.post(self.urls['post_checkCode'], data=data)

            if resp.status_code != 200:
                settings.logger.error("crawl post check page failed!")
                count += 1
                continue
            if resp.content[10] == 't':
                data = {'checkNo': ck_code, 'entName': self.ent_number}
                resp = self.reqst.post(self.urls['post_checkCode2'], data=data)
                soup = BeautifulSoup(resp.text, "html5lib")
                div = soup.find("div", {"style": "height:500px;"})
                a = div.find("a")
                if a:
                    self.company_id = a["href"].split('?')[1]
                    return True
                else:
                    return None

            else:
                settings.logger.error("crawl post check page failed!")
                count += 1
                continue
        return False

    def crack_check_code(self):
        """破解验证码
        :return 破解后的验证码
        """
        resp = self.reqst.get(self.urls['get_checkcode'])
        if resp.status_code != 200:
            settings.logger.error('failed to get get_checkcode')
            return None

        time.sleep(random.uniform(2, 4))

        self.write_file_mutex.acquire()
        with open(self.ckcode_image_path, 'wb') as f:
            f.write(resp.content)
        try:
            ckcode = self.code_cracker.predict_result(self.ckcode_image_path)
        except Exception as e:
            settings.logger.warn('exception occured when crack checkcode')
            ckcode = ('', '')
        finally:
            pass
        self.write_file_mutex.release()

        return ckcode[1]

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

    def crawl_ind_comm_pub_pages(self):
        """爬取工商公示信息
        """
        url = "%s%s" % (self.urls['ind_comm_pub_skeleton'], self.company_id)
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            settings.logger.error('failed to get ind_comm_pub_skeleton')
        else:
            settings.logger.info('succcess to get ind_comm_pub_skeleton')
        self.parser.parse_ind_comm_pub_pages(resp.content)

        # return resp.content

    def crawl_ent_pub_pages(self):
        """爬取企业公示信息
        """
        url ="%s%s" % (self.urls['ent_pub_skeleton'], self.company_id)
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            settings.logger.error('failed to get ent_pub_skeleton')
        else:
            settings.logger.info('success to get ent_pub_skeleton')
        self.parser.parse_ent_pub_pages(resp.content)

        # return resp.content

    def crawl_other_dept_pub_pages(self):
        """爬取其他部门公示信息
        """
        url = "%s%s" % (self.urls['other_dept_pub_skeleton'], self.company_id)
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            settings.logger.error('failed to get other_dept_pub_skeleton')
        else:
            settings.logger.info('success to get other_dept_pub_skeleton')
        self.parser.crawl_other_dept_pub_pages(resp.content)

        # return resp.content

    def crawl_judical_assist_pub_pages(self):
        """爬取司法协助信息
        """
        url = "%s%s" % (self.urls['judical_assist_skeleton'], self.company_id)
        resp = self.reqst.get(url)
        if resp.status_code != 200:
            settings.logger.error('failed to get judical_assist_skeleton')
        else:
            settings.logger.info('success to get judical_assist_skeleton')
        self.parser.parse_judical_assist_pub_pages(resp.content)

        # return resp.content


class QinghaiParser(Parser):
    """青海工商页面的解析类
    """
    def __init__(self, crawler):
        self.crawler = crawler

    def parse_ind_comm_pub_pages(self, page):
        """解析工商公示信息-页面，在青海的页面中，工商公示信息所有信息都通过一个http get返回
        """
        soup = BeautifulSoup(page, "html5lib")
        # 一类表
        name_table_map = {
            u'基本信息': 'ind_comm_pub_reg_basic',  # 登记信息-基本信息
            u'清算信息': 'ind_comm_pub_arch_liquidation',  # 备案信息-清算信息
        }

        for table in soup.find_all('table'):
            list_table_title = table.find("th")
            if not list_table_title:
                continue

            if name_table_map.has_key(list_table_title.text):
                table_name = name_table_map[list_table_title.text]
                settings.logger.info('crawler to get %s', table_name)
                self.crawler.json_dict[table_name] = self.parse_table1(table)

        # 二类表
        id_table_map = {
            'altDiv': 'ind_comm_pub_reg_modify',  # 登记信息-变更信息
            # 'memDiv': 'ind_comm_pub_arch_key_persons',  # 备案信息-主要人员信息
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

            table = soup.find("div", {"id": table_id})
            if not table:
                continue
            td = table.find_all("td")
            if td:
                id = self.crawler.company_id.split("=")[1]
                settings.logger.info('crawler to get %s', table_name)
                self.crawler.json_dict[table_name] = self.parse_table2(table, table_name, id, 0)[0]
            else:
                self.crawler.json_dict[table_name] = []  # 若表格内没有td则视为空
                continue

        # 股东信息
        div = soup.find("div", {"id": "invDiv"})
        if div:
            settings.logger.info('crawler to get ind_comm_pub_reg_shareholder')
            id = self.crawler.company_id.split("=")[1]
            return_table = self.parse_table2(div, 'ind_comm_pub_reg_shareholder', id, 1)
            if return_table[1] != "True":
                for i in range(0, len(return_table[1])):
                    return_table[0][i][u'详情'] = self.get_shareholder_detail(return_table[1][i])
            self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = return_table[0]
        else:
            self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = []

        # 动产抵押登记信息
        div = soup.find("div", {"id": "mortDiv"})
        if div:
            settings.logger.info('crawler to get ind_comm_pub_movable_property_reg')
            id = self.crawler.company_id.split("=")[1]
            return_table = self.parse_table2(div, 'ind_comm_pub_movable_property_reg', id, 1)
            if return_table[1] != "True":
                for i in range(0, len(return_table[1])):
                    return_table[0][i][u'详情'] = self.get_movable_property_reg_detail(return_table[1][i])
            self.crawler.json_dict['ind_comm_pub_movable_property_reg'] = return_table[0]
        else:
            self.crawler.json_dict['ind_comm_pub_movable_property_reg'] = []

         # 备案信息-主要人员信息
        div = soup.find("div", {"id": "memDiv"})
        if div:
            settings.logger.info('crawler to get ind_comm_pub_movable_property_reg')
            table_th1 = div.previous_sibling.previous_sibling
            company_id1 = self.crawler.company_id.split("=")[1]
            table_th_trs = table_th1.find_all("tr")
            list_th = [th for th in table_th_trs[1].stripped_strings]
            if div.next_sibling.next_sibling and str(div.next_sibling.next_sibling.name) == 'table':
                table_page = div.next_sibling.next_sibling
                table_page_tol = table_page.find_all("a")
                table_save = []

                for i in range(1, len(table_page_tol)+1):
                    url = '%s%s%s%s%s' % (self.crawler.urls['ind_comm_pub_arch_key_persons'], "pno=", i, '&mainId=', company_id1)
                    # print "url", url
                    rep = requests.get(url)
                    soup = BeautifulSoup(rep.text, "html5lib")

                    table = soup.find("table")
                    # print "主要人员", table

                    trs = table.find_all("tr")

                    for tr in trs:
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
        else:
            self.crawler.json_dict['ind_comm_pub_arch_key_persons'] = []

    def parse_ent_pub_pages(self, page):
        soup = BeautifulSoup(page, "html5lib")

        # 四类表
        name_table_map = {
            u'股权变更信息': 'ent_pub_equity_change',
            u'变更信息': 'ent_pub_reg_modify',
            u'行政许可信息': 'ent_pub_administration_license',
            u'知识产权出质登记信息': 'ent_pub_knowledge_property',
            u'行政处罚信息': 'ent_pub_administration_sanction',
        }

        for table in soup.find_all('table'):
            list_table_title = table.find("th")
            if not list_table_title:
                continue
            if name_table_map.has_key(list_table_title.text):
                table_name1 = name_table_map[list_table_title.text]
                settings.logger.info('crawler to get %s', table_name1)
                self.crawler.json_dict[table_name1] = self.ana_table4(table)

        # 股东及出资信息
        gdDiv = soup.find("div", {"id": "gdDiv"})
        if gdDiv:
            settings.logger.info('crawler to get ent_pub_shareholder_and_investment')
            table = gdDiv.find("table")
            self.crawler.json_dict['ent_pub_shareholder_and_investment'] = self.coarse_page_table(table)

        #企业年报
        qiyenianbao = soup.find("div", {"id": "qiyenianbao"})
        table_th1 = []
        table_save_all = []

        table_ths = qiyenianbao.find_all("th")
        for th in table_ths:
            if 'colspan' in th.attrs:
                continue
            table_th1.append(th.text)

        table_trs = qiyenianbao.find_all("tr")
        for tr in table_trs[2:]:
            table_ts = {}
            table_td1 = []
            content_tds = tr.find_all("td")
            for table_td_text in content_tds:
                table_td1.append(table_td_text.text.strip())
            for i in range(0, len(table_th1)):
                table_ts[table_th1[i]] = table_td1[i]
            table_detail = {}
            a = qiyenianbao.find_all("a")
            if a:
                for a1 in a:
                    m = re.search(r'id=(.*?)\"', str(a1))
                    args = m.group(1)
                    host = 'http://218.95.241.36/QueryYearExamineDetail.jspx?id='
                    url = '%s%s' % (host, args)
                    rep = requests.get(url)
                    soup = BeautifulSoup(rep.content, 'html5lib')

                    # wrap = {}
                    tables = soup.find_all("table")
                    for table in tables:
                        table_tiiles = table.find("th")
                        if table_tiiles.attrs['style'] == 'text-align:center;color:red':
                            table_tiiles = table_tiiles.parent
                            table_tiiles = table_tiiles.next_sibling.next_sibling

                        name_table_map2 = [u'企业资产状况信息', u'企业基本信息', u'基本信息']
                        if table_tiiles.text in name_table_map2:
                            table_detail[table_tiiles.text] = self.parse_table1(table)
                    # table_detail.append(wrap)


                    # 四类表
                    name_table_map = [u'网站或网店信息', u'股东及出资信息', u'行政许可情况', u'对外投资信息',
                                      u'对外提供保证担保信息', u'股权变更信息', u'修改记录']

                    for table in soup.find_all('table'):
                        list_table_title = table.find("th")
                        if list_table_title.text in name_table_map:
                            table_trs = table.find_all("tr")
                            table_th = [th for th in table_trs[1].stripped_strings]

                            table_c = []
                            for table_tr in table_trs[2:-1]:
                                tds = table_tr.find_all("td")
                                table_td = [td.text.strip() for td in tds]

                                table_save = {}
                                wrap = {}
                                for i in range(0, len(table_td)):
                                    table_save[table_th[i]] = table_td[i]
                                table_c.append(table_save)
                            table_detail[list_table_title.text] = table_c
                            # table_detail.append(wrap)

                # cont = table_ts[u'报送年度']
                table_ts[u'详情'] = table_detail

            table_save_all.append(table_ts)

        self.crawler.json_dict['ent_pub_ent_annual_report'] = table_save_all

    def crawl_other_dept_pub_pages(self, page):

        soup = BeautifulSoup(page, "html5lib")
        company_id = self.crawler.company_id.split("=")[1]
        id_table_map = {
            'licenseRegDiv': 'other_dept_pub_administration_license',  # 行政许可信息
            'xzcfDiv': 'other_dept_pub_administration_sanction',  # 行政处罚信息
        }
        table_ids = id_table_map.keys()
        for table_id in table_ids:
            table_name = id_table_map[table_id]

            table = soup.find("div", {"id": table_id})

            if not table:
                self.crawler.json_dict[table_name] = []
                continue
            if table_id is 'xzcfDiv':
                table = table.next_sibling.next_sibling
                self.crawler.json_dict[table_name] = self.parse_table2(table, table_name, company_id, 0)[0]
            else:
                 self.crawler.json_dict[table_name] = self.parse_table2(table, table_name, company_id, 0)[0]

    def parse_judical_assist_pub_pages(self, page):

        soup = BeautifulSoup(page, "html5lib")
        company_id = self.crawler.company_id.split("=")[1]
        id_table_map = {
            'EquityFreezeDiv': 'judical_assist_pub_shareholder_modify',  # 股东变更信息
            'xzcfDiv': 'judical_assist_pub_equity_freeze',  # 股权冻结信息
        }
        table_ids = id_table_map.keys()

        for table_id in table_ids:
            table_name = id_table_map[table_id]

            div = soup.find("div", {"id": table_id})
            table = div.next_sibling.next_sibling

            if not table:
                self.crawler.json_dict[table_name] = []
                continue

            self.crawler.json_dict[table_name] = self.parse_table2(table, table_name, company_id, 0)[0]

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

    def parse_table2(self, table, table_name, company_id, status):

        # 获得表头
        previous_table = table.previous_sibling.previous_sibling
        table_title = previous_table.find("tr")

        # 获得列名
        table_column = table_title.next_sibling.next_sibling

        # 将列名存在列表里
        table_columns = [column for column in table_column.stripped_strings]

        # 获得页数
        if table.next_sibling.next_sibling:
            table_page = table.next_sibling.next_sibling
            table_page_tol = table_page.find_all("a")
            if 'id' in table.next_sibling.next_sibling.attrs:
                if table.next_sibling.next_sibling.attrs['id'] == 'invPagination':
                   if self.crawler.urls.has_key(table_name):

                    for j in range(1, len(table_page_tol)+1):
                        table_ts = []
                        content_tr = []
                        url = '%s%s%s%s%s' % (self.crawler.urls[table_name], "pno=", j, '&mainId=', company_id)
                        rep = requests.get(url)
                        soup = BeautifulSoup(rep.text, "html5lib")
                        table = soup.find("table")
                        table_save = self.get_td(table, table_columns)
                        tr = table.find_all("tr")
                        content_tr.extend(tr)
                        table_ts.extend(table_save)

                        return [table_ts, content_tr]

        if table.next_sibling.next_sibling and str(table.next_sibling.next_sibling.name) == 'table':
            table_page = table.next_sibling.next_sibling
            table_page_tol = table_page.find_all("a")
            if int(len(table_page_tol)) <= 1 and status == 0:

                table_save = self.get_td(table, table_columns)
                return [table_save, 'True']

            else:
                if self.crawler.urls.has_key(table_name):
                    table_ts = []
                    content_tr = []
                    for j in range(1, len(table_page_tol)+1):

                        url = '%s%s%s%s%s' % (self.crawler.urls[table_name], "pno=", j, '&mainId=', company_id)
                        rep = requests.get(url)
                        soup = BeautifulSoup(rep.text, "html5lib")
                        table = soup.find("table")
                        table_save = self.get_td(table, table_columns)
                        tr = table.find_all("tr")
                        content_tr.extend(tr)
                        table_ts.extend(table_save)

                    return [table_ts, content_tr]
        else:
            table_save = self.get_td(table, table_columns)
            return [table_save, 'True']

    def get_td(self, table, table_columns):
        # 获取内容表的每一列，并将每一列做成一个字典
        content_trs = table.find_all("tr")
        content_td = table.find_all("td")
        table_save = []
        if content_trs and content_td:
            for content_tr in content_trs:
                content_tds = content_tr.find_all("td")
                list_td = []
                test = {}
                for content_td in content_tds:
                    list_td.append(content_td.text.strip())
                for i in range(0, len(table_columns)):
                    test[table_columns[i]] = list_td[i]
                table_save.append(test)
            return table_save
        else:
            return []

    def get_shareholder_detail(self, content_tr):

        if not content_tr.find("a"):
            return

        link = content_tr.find("a")
        m = re.search(r'id=(.\d+)', str(link))

        int1 = m.group(1)
        url1 = '%s%s' %('http://218.95.241.36/queryInvDetailAction.jspx?id=', int1)
        rep1 = requests.get(url1)
        soupn = BeautifulSoup(rep1.text, "html5lib")

        table = soupn.find("table")
        table_title1 = table.find("th").text  # 获取表头
        detail = {}
        detail[table_title1] = self.coarse_page_table(table)

        return detail

    def get_movable_property_reg_detail(self, content_tr):

        link = content_tr.find("a")
        m = re.search(r'id=(.\d+)', str(link))
        int1 = m.group(1)
        url1 = '%s%s' %('http://218.95.241.36/mortInfoDetail.jspx?id=', int1)
        rep1 = requests.get(url1)
        soupn = BeautifulSoup(rep1.text, "html5lib")

        name_table_map1 = [u"抵押权人概况"]
        name_table_map2 = [u'动产抵押登记信息', u'被担保债权概况']
        # table_detail = []
        wrap = {}
        for table in soupn.find_all('table'):
            list_table_title = table.find("th")

            if list_table_title and list_table_title.text in name_table_map2:
                wrap[list_table_title.text] = self.parse_table1(table)
            if list_table_title and list_table_title.text in name_table_map1:
                wrap[list_table_title.text] = self.ana_table4(table)
        table = soupn.find("div", {"id": "guaDiv"})
        if table:
            wrap[u"抵押物概况"] = self.parse_table2(table, 1, 0, 0)[0]
        # table_detail.append(wrap)
        return wrap

    def ana_table4(self, table):
        ths = table.find_all("th")
        list_th = []
        trs = table.find_all("tr")
        list_tr = []
        table_all = []
        for th in ths:
            if 'colspan' in th.attrs:
                continue
            else:
                list_th.append(th.text)
        for tr in trs:
            list_tr.append(tr)
        for con_tr in list_tr[2:]:
            list_td = []
            table3 = {}
            content_tds = con_tr.find_all("td")
            for table_td_text in content_tds:
                list_td.append(table_td_text.text.strip())

            for i in range(0, len(list_th)):
                table3[list_th[i]] = list_td[i]
            table_all.append(table3)
        return table_all

    def coarse_page_table(self, table):

        colspan_list = []  # 跨列的列数
        list_title_th = []  # 第一行不跨列的列名
        list_th = []  # 第二行的列名

        table_trs = table.find_all("tr")
        list_tr = [tr for tr in table_trs]
        table_title_wraps = list_tr[1].find_all("th")

        for title_wrap in table_title_wraps:
            if 'colspan' in title_wrap.attrs:
                for colspan in title_wrap['colspan']:
                    colspan_list.append(int(colspan))
            else:
                list_title_th.append(title_wrap.text)

        table_title = list_tr[2].find_all("th")
        for title_wrap in table_title:
            list_th.append(title_wrap.text)
        sum = 0
        for i in colspan_list:
            sum = sum + i

        total = []  # 若有多行td
        total_th = list_title_th + list_th  # 总列名

        for tr in table_trs[3:]:
            table_td = tr.find_all("td")
            list_td = [td.text.strip() for td in table_td]  # 表格内容列表
            table_save = {}  # 保存的表格
            if len(list_td) == len(total_th):
                for i in range(0, len(list_title_th)):
                    table_save[list_title_th[i]] = list_td[i]

                del list_td[0:len(list_title_th)]
                list_test = []
                table_test = {}
                for i in range(0, sum):
                    if list_th[i] == "公示日期":
                        if table_test.has_key("认缴_公示日期"):
                            table_test["实缴_公示日期"] = list_td[i]
                            continue
                        else:
                            table_test["认缴_公示日期"] = list_td[i]
                            continue
                    table_test[list_th[i]] = list_td[i]
                list_test.append(table_test)
                table_save["list"] = list_test

                total.append(table_save)
            elif len(list_td) == sum:
                list_test = []
                table_test = {}
                for i in range(0, sum):
                    if list_th[i] == "公示日期":
                        if table_test.has_key("认缴_公示日期"):
                            table_test["实缴_公示日期"] = list_td[i]
                            continue
                        else:
                            table_test["认缴_公示日期"] = list_td[i]
                            continue
                    table_test[list_th[i]] = list_td[i]
                list_test.append(table_test)
                table_save["list"] = list_test

                total.append(table_save)
            else:
                list_test = []
                table_test = {}
                del list_th[0: colspan_list[0]]
                for i in range(0, sum):
                    if list_th[i] == "公示日期":
                        if table_test.has_key("认缴_公示日期"):
                            table_test["实缴_公示日期"] = list_td[i]
                            continue
                        else:
                            table_test["认缴_公示日期"] = list_td[i]
                            continue
                    table_test[list_th[i]] = list_td[i]
                list_test.append(table_test)
                table_save["list"] = list_test

                total.append(table_save)

        return total

if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    QinghaiCrawler.code_cracker = CaptchaRecognition('qinghai')
    crawler = QinghaiCrawler('./enterprise_crawler/qinghai.json')
    enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/qinghai.txt')
    # enterprise_list = ['630000100008079']

    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('############   Start to crawl enterprise with id %s   ################\n' % ent_number)
        crawler.run(ent_number=ent_number)
