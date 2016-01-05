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

            'ind_comm_pub_reg_shareholder': 'http://gsxt.hljaic.gov.cn/QueryInvList.jspx?',# 股东信息
            'ind_comm_pub_reg_modify': 'http://gsxt.hljaic.gov.cn/QueryAltList.jspx?',  # 变更信息翻页
            'ind_comm_pub_arch_key_persons': 'http://gsxt.hljaic.gov.cn/QueryMemList.jspx?',  # 主要人员信息翻页

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

        # self.crawl_ind_comm_pub_pages(result_ID)
        self.crawl_ent_pub_pages(result_ID)
        # self.crawl_other_dept_pub_pages(result_ID)
        # self.crawl_judical_assist_pub_pages(result_ID)

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

    # def crawl_ind_comm_pub_pages(self, result_ID):
    #     """爬取工商公示信息
    #     """
    #     url = "%s%s" % (HeilongjiangCrawler.urls['ind_comm_pub_skeleton'], result_ID)
    #     resp = self.reqst.get(url)
    #     self.parser.parse_ind_comm_pub_pages(resp.content, result_ID)
    #
    #     return resp.content
    #
    def crawl_ent_pub_pages(self, result_ID):
        """爬取企业公示信息
        """
        url ="%s%s" % (HeilongjiangCrawler.urls['ent_pub_skeleton'], result_ID)
        resp = self.reqst.get(url)
        self.parser.parse_ent_pub_pages(resp.content)

        return resp.content

    # def crawl_other_dept_pub_pages(self, result_ID):
    #     """爬取其他部门公示信息
    #     """
    #     url = "%s%s" % (HeilongjiangCrawler.urls['other_dept_pub_skeleton'], result_ID)
    #     resp = self.reqst.get(url)
    #     self.parser.crawl_other_dept_pub_pages(resp.content, result_ID)
    #
    #     return resp.content

    def crawl_judical_assist_pub_pages(self, result_ID):
        """爬取司法协助信息
        """
        url = "%s%s" % (HeilongjiangCrawler.urls['judical_assist_skeleton'], result_ID)
        resp = self.reqst.get(url)

        # print resp.content


class HeilongjiangParser(Parser):
    """北京工商页面的解析类
    """
    def __init__(self, crawler):
        self.crawler = crawler

    def parse_ind_comm_pub_pages(self, page, result_ID):
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
            if list_table_title is None:
                continue

            if name_table_map.has_key(list_table_title.text):
                table_name = name_table_map[list_table_title.text]

                self.crawler.json_dict[table_name] = self.ana_table1(table)

        # 二类表
        id_table_map = {
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

            table = soup.find("div", {"id": table_id})
            if table is None:
                self.crawler.json_dict[table_name] = []
                continue
            td = table.find_all("td")
            if td:
                id = result_ID.split("=")[1]
                self.crawler.json_dict[table_name] = self.ana_table2(table, table_name, id)
            else:
                self.crawler.json_dict[table_name] = []  # 若表格内没有td则视为空
                continue

        # 股东信息
        div = soup.find("div", {"id": "invDiv"})
        if div:
            id = result_ID.split("=")[1]
            return_table = self.ana_table2(div, 'ind_comm_pub_reg_shareholder', id)
            for i in range(0, len(return_table[1])):
                return_table[0][i][u'详情'] = self.get_shareholder_detail(return_table[1][i])
            self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = return_table[0]
        else:
            self.crawler.json_dict['ind_comm_pub_reg_shareholder'] = []

    def parse_ent_pub_pages(self, page):
        soup = BeautifulSoup(page, "html5lib")

        # 一类表
        name_table_map = {
            u'股权变更信息': 'ent_pub_equity_change',
            u'变更信息': 'ent_pub_reg_modify',
            u'行政许可信息': 'ent_pub_administration_license',
            u'知识产权出质登记信息': 'ent_pub_knowledge_property',
            u'行政处罚信息': 'ent_pub_administration_sanction',
        }

        for table in soup.find_all('table'):
            list_table_title = table.find("th")
            if list_table_title is None:
                continue
            if name_table_map.has_key(list_table_title.text):
                table_name1 = name_table_map[list_table_title.text]
                self.crawler.json_dict[table_name1] = self.ana_table4(table)


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
            table_td1 = [td for td in tr.stripped_strings]
            for i in range(0, len(table_th1)-1):
                table_ts[table_th1[i]] = table_td1[i]

            a = qiyenianbao.find_all("a")
            if a:
                for a1 in a:
                    table_detail = []
                    re1='.*?'	# Non-greedy match on filler
                    re2='(\\d+)'	# Integer Number 1
                    re3='((?:[a-z][a-z]*[0-9]+[a-z0-9]*))'	# Alphanum 1

                    rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
                    m = rg.search(str(a1))
                    int1 = m.group(1)
                    alphanum1 = m.group(2)
                    host = 'http://gsxt.hljaic.gov.cn/QueryYearExamineDetail.jspx?id='
                    url = '%s%s' % (host, int1+alphanum1)
                    rep = requests.get(url)
                    soup = BeautifulSoup(rep.content, 'html5lib')

                    # 企业基本信息
                    qiyexinxi = soup.find("table", {"style": "border-right: solid 1px grey;"})

                    table_ths = qiyexinxi.find_all("th")
                    table_th = [th.text for th in table_ths[2:]]

                    table_tds = qiyexinxi.find_all("td")
                    table_td = [td.text for td in table_tds]

                    table_save = {}
                    wrap = {}
                    for i in range(0, len(table_td)):
                        table_save[table_th[i]] = table_td[i]
                    wrap[u'企业基本信息'] = table_save
                    table_detail.append(wrap)

                    # 企业资产状况信息
                    tables = soup.find_all("table")
                    for table in tables:
                        table_tiiles = table.find("th")
                        for table_tiile in table_tiiles:
                            if u"企业资产状况信息" in table_tiile:

                                table_ths = table.find_all("th")
                                table_th = [th.text for th in table_ths[1:]]

                                table_tds = table.find_all("td")
                                table_td = [td.text for td in table_tds]

                                table_save = {}
                                wrap = {}
                                for i in range(0, len(table_td)):
                                    table_save[table_th[i]] = table_td[i]
                    wrap[u'企业资产状况信息'] = table_save
                    table_detail.append(wrap)





                    # 一类表
                    name_table_map = {
                        u'网站或网店信息': 'ind_com_reg_basic', # 登记信息-基本信息
                        u'股东及出资信息': 'icomm_pub_arch_liquidation', # 备案信息-清算信息
                        u'对外投资信息': '111 s sds11',
                        u'对外提供保证担保信息': '111dsadad11',
                        u'股权变更信息': '23dsqq3',
                        u'修改记录': '11weee1',

                    }

                    for table in soup.find_all('table'):
                        list_table_title = table.find("th")

                        if name_table_map.has_key(list_table_title.text):
                            table_name = name_table_map[list_table_title.text]
                            table_trs = table.find_all("tr")
                            table_th = [th for th in table_trs[1].stripped_strings]

                            table_c = []
                            for tr in table_trs[2:]:
                                tds = tr.find_all("td")
                                table_td = [td.text for td in tds]

                                table_save = {}
                                wrap = {}
                                for i in range(0, len(table_td)):
                                    table_save[table_th[i]] = table_td[i]
                                table_c.append(table_save)
                            wrap[list_table_title.text] = table_c
                            table_detail.append(wrap)
            #
            # print "table_detail22222", table_detail
            cont = table_ts[u'报送年度']
            # print cont
            table_ts[u'报送年度'] = [cont,table_detail]
            # print table_ts

            table_save_all.append(table_ts)
        # print table_save_all
        self.crawler.json_dict['ent_pub_ent_annual_report'] = table_save_all

    def crawl_other_dept_pub_pages(self, page, result_ID):

        soup = BeautifulSoup(page, "html5lib")
        id_table_map = {
            'licenseRegDiv': '111111111',  # 登记信息-变更信息
            # 'xzcfDiv': '2222222',  # 备案信息-主要人员信息
        }
        table_ids = id_table_map.keys()
        for table_id in table_ids:
            table_name = id_table_map[table_id]

            table = soup.find("div", {"id": table_id})
            if table is None:
                self.crawler.json_dict[table_name] = []
                continue
            id = result_ID.split("=")[1]
            aaaa = self.ana_table2(table, table_name, id)
            print aaaa
            self.crawler.json_dict[table_name] = self.ana_table2(table, table_name, id)
    def ana_table1(self, table):
        '''读取一类表,返回字典 '''
        ths = table.find_all("th")
        list_th = []
        tds = table.find_all("td")
        list_td = []
        table_save = {}
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
            table_save[list_th[i]] = list_td[i-1]

        return table_save
    def ana_table2(self, table, table_name, id):

        # 获得表头
        previous_table = table.previous_sibling.previous_sibling
        table_title = previous_table.find("tr")

        # 获得列名
        table_column = table_title.next_sibling.next_sibling

        # 将列名存在列表里
        table_columns = [column for column in table_column.stripped_strings]

        # 获得列名列表长度
        # len_colums = len(table_columns)
        # 获得页数
        if table.next_sibling.next_sibling:
            table_page = table.next_sibling.next_sibling
            table_page_tol = table_page.find_all("a")
            if int(len(table_page_tol)) <= 1:

                table_save = self.get_td(table, table_columns)

                return table_save

            else:
                if HeilongjiangCrawler.urls.has_key(table_name):
                    table_ts = []
                    content_tr = []
                    for j in range(1, len(table_page_tol)+1):
                        url = '%s%s%s%s%s' % (HeilongjiangCrawler.urls[table_name], "pno=", j, '&mainId=', id)
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
            return table_save
    def get_td(self, table, table_columns):
        # 获取内容表的每一列，并将每一列做成一个字典
        content_trs = table.find_all("tr")
        if content_trs:
            table_save = []
            for content_tr in content_trs:
                table_tr = {}
                list_content_tr = [content for content in content_tr.stripped_strings]
                for i in range(0, len(table_columns)):
                    table_tr[table_columns[i]] = list_content_tr[i]
                table_save.append(table_tr)

            # 将表格信息存储到json中
            return table_save
        else:
            return []

    def get_shareholder_detail(self, content_tr):

        link = content_tr.find("a")
        re1 = '.*?'	 # Non-greedy match on filler
        re2 = '\\d+'  # Uninteresting: int
        re3 = '.*?' 	# Non-greedy match on filler
        re4 = '(\\d+)'	 # Integer Number 1

        rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
        m = rg.search(str(link))

        int1 = m.group(1)
        url1 = '%s%s' %('http://gsxt.hljaic.gov.cn/queryInvDetailAction.jspx?id=', int1)
        detail = {}
        rep1 = requests.get(url1)
        soupn = BeautifulSoup(rep1.text, "html5lib")
        table_thn = soupn.find_all("th")
        list_th = []
        colspan_th = []
        test1 = {}
        test2 = {}
        colspan_list = []
        for th in table_thn:
            if 'colspan' in th.attrs:
                for colspan in th['colspan']:
                    colspan_th.append(th.text)
                    colspan_list.append(int(colspan))
                continue
            else:
                list_th.append(th.text)

        table_tdn = soupn.find_all("td")
        list_td = []
        for td in table_tdn:
                list_td.append(td.text)
        total1 = 0
        for total in colspan_list[1:]:
            total1 = total + total1
        for k in range(0, len(list_th)-total1):
            detail[list_th[k]] = list_td[k]
        for k in range(3, 6):
            test1[list_th[k]] = list_td[k]
            detail[colspan_th[1]] = test1
        for k in range(6, 9):
            test2[list_th[k]] = list_td[k]
            detail[colspan_th[2]] = test2
        return detail

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
            for td in con_tr.stripped_strings:
                list_td.append(td)
            for i in range(0, len(list_th)):
                table3[list_th[i]] = list_td[i]
            table_all.append(table3)
        return table_all

    def coarse_page_table(self):

        colspan_list = []
        colspan_th = []
        list_title_th = []
        list_td = []
        table_test = {}


        table_tr = table.find_all("tr")
        list_tr = [tr for tr in table_tr]
        table_title_wraps = list_tr[1].find_all("th")

        for title_wrap in table_title_wraps:
            if 'colspan' in title_wrap.attrs:
                for colspan in th['colspan']:
                    colspan_list.append(int(colspan))
                    colspan_th.append(th.text)
            else:
                list_title_th.append(title_wrap.text)
        table_title = list_tr[2].find_all("th")
        for title_wrap in table_title:
            list_th.append(title_wrap.text)

        table_td = table.find_all("td")
        list_td = [td for td in table_td]

        table_save = {}
        for i in range(0, len(list_title_th)):
            table_save[list_title_th[i]] = list_td[i]

        for i in colspan_list[1:]:
            i = 3,3
            for j in range(0, i-1):
                table_test[list_th[j]] = list_td[j+len(list_title_th)]





        # for i in colspan_list[1:]:
        #     i = 3,3
        #
        #     for j in len(colspan_list):
        #     table_save[colspan_th[j]] =





if __name__ == '__main__':
    from CaptchaRecognition import CaptchaRecognition
    import run
    run.config_logging()
    HeilongjiangCrawler.code_cracker = CaptchaRecognition('qinghai')
    crawler = HeilongjiangCrawler('./enterprise_crawler/heilongjiang.json')
    # enterprise_list = CrawlerUtils.get_enterprise_list('./enterprise_list/heilongjiang.txt')
    # enterprise_list = ['230184600287668']
    enterprise_list = ['230100100019556']
    for ent_number in enterprise_list:
        ent_number = ent_number.rstrip('\n')
        settings.logger.info('###################   Start to crawl enterprise with id %s   ###################\n' % ent_number)
        crawler.run(ent_number=ent_number)
