#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import requests
import logging
import os
import sys
import time
import re
ENT_CRAWLER_SETTINGS=os.getenv('ENT_CRAWLER_SETTINGS')
if ENT_CRAWLER_SETTINGS and ENT_CRAWLER_SETTINGS.find('settings_pro') >= 0:
    import settings_pro as settings
else:
    import settings

import json
import codecs
import unittest
import threading
from bs4 import BeautifulSoup
import CaptchaRecognition as CR
import hashlib #验证码是MD5加密的，调用此包

urls = {
    'host': 'http://218.57.139.24/pub/',
    'webroot' : 'http://218.57.139.24/',
    'page_search': 'http://218.57.139.24/',
    'page_Captcha': 'http://218.57.139.24/securitycode',
    'page_showinfo': 'http://218.57.139.24/pub/indsearch',
    'checkcode':'http://218.57.139.24/pub/indsearch',
}

headers = { #'Connetion': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36",
            }

class ShandongCrawler(object):
    #多线程爬取时往最后的json文件中写时的加锁保护
    write_file_mutex = threading.Lock()

    def __init__(self, json_restore_path):
        self.html_search = None
        self.html_showInfo = None
        self.Captcha = None
        #self.path_captcha = './Captcha.png'

        self.CR = CR.CaptchaRecognition("shandong")
        self.requests = requests.Session()
        self.requests.headers.update(headers)
        self.ents = []
        self.json_dict={}
        self.json_restore_path = json_restore_path
        self.csrf = ""
        #验证码图片的存储路径
        self.path_captcha = settings.json_restore_path + '/shandong/ckcode.jpeg'
        #html数据的存储路径
        self.html_restore_path = settings.html_restore_path + '/shandong/'


    # 破解搜索页面
    def crawl_page_search(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            settings.logger.error(u"Something wrong when getting the url:%s , status_code=%d", url, r.status_code)
            return
        r.encoding = "utf-8"
        #settings.logger.debug("searchpage html :\n  %s", r.text)
        self.html_search = r.text

    #分析 展示页面， 获得搜索到的企业列表
    def analyze_showInfo(self, page):
        Ent = []
        soup = BeautifulSoup(page, "html5lib")
        divs = soup.find_all("div", {"class":"list"})
        for div in divs:
            Ent.append(div.ul.li.a['href'])
        self.ents = Ent

    # 破解验证码页面
    def crawl_page_captcha(self, url_Captcha, url_CheckCode,url_showInfo,  textfield= '370000018067809'):

        count = 0
        while True:
            count+= 1
            r = self.requests.get( url_Captcha)
            if r.status_code != 200:
                settings.logger.error(u"Something wrong when getting the Captcha url:%s , status_code=%d", url_Captcha, r.status_code)
                return
            self.Captcha = r.content
            #settings.logger.debug("Captcha page html :\n  %s", self.Captcha)
            if self.save_captcha():
                settings.logger.info("Captcha is saved successfully \n" )
                result = self.crack_captcha()
                print result
                secode = hashlib.md5(str(result)).hexdigest() # MD5 encode
                if not self.html_search:
                    settings.logger.error(u"There is no front page")
                soup = BeautifulSoup(self.html_search, 'html5lib')
                csrf = soup.find('input', {'name':'_csrf'})['value']
                self.csrf = csrf
                datas= {
                        'kw' : textfield,
                        '_csrf': csrf,
                        'secode': secode,
                }
                #response = self.get_check_response(url_CheckCode, datas)
                page=  self.crawl_page_by_url_post(url_CheckCode, datas)['page']
                # 如果验证码正确，就返回一种页面，否则返回主页面

                if self.is_search_result_page(page) :
                    self.analyze_showInfo(page)
                    break
                else:
                    settings.logger.debug(u"crack Captcha failed, the %d time(s)", count)
        return

    # 判断是否成功搜索页面
    def is_search_result_page(self, page):
        soup = BeautifulSoup(page, 'html5lib')
        divs = soup.find('div', {'class':'list'})
        return divs is not None

    #调用函数，破解验证码图片并返回结果
    def crack_captcha(self):
        if os.path.exists(self.path_captcha) is False:
            settings.logger.error(u"Captcha path is not found\n")
            return
        result = self.CR.predict_result(self.path_captcha)
        return result[1]
        #print result
    # 保存验证码图片
    def save_captcha(self):
        url_Captcha = self.path_captcha
        if self.Captcha is None:
            settings.logger.error(u"Can not store Captcha: None\n")
            return False
        self.write_file_mutex.acquire()
        f = open(url_Captcha, 'w')
        try:
            f.write(self.Captcha)
        except IOError:
            settings.logger.debug("%s can not be written", url_Captcha)
        finally:
            f.close
        self.write_file_mutex.release()
        return True
    """
        The following enterprises in ents
       2. for each ent: decide host so that choose e urls
        4. for eah url, iterate item in tabs
    """
    def crawl_page_main(self ):
        sub_json_dict= {}
        if not self.ents:
            settings.logger.error(u"Get no search result\n")
        try:
            for ent in self.ents:
                m = re.match('http', ent)
                if m is None:
                    ent = urls['host']+ ent
                settings.logger.debug(u"ent url:%s\n"% ent)
                #ent_num = ent[ent.index('entId=')+6 :]
                #工商公示信息
                url = ent
                #html_to_file('next.html', page)
                entpripid = ent[ent.rfind('/')+1:]
                temp = ent[:ent.rfind('/')]
                enttype =  temp[temp.rfind('/')+1 :]
                sub_json_dict.update(self.crawl_ind_comm_pub_pages(url))
                # 企业公示信息 http://218.57.139.24/pub/qygsdetail/
                #url = url.replace('gsgsdetail', 'qygsdetail')
                #url = urls['host'] + 'qygsdetail/'+ enttype+'/'+entpripid
                # sub_json_dict.update(self.crawl_ent_pub_pages(url))
                # #其他部门http://218.57.139.24/pub/qtgsdetail/
                # url = url.replace('qygsdetail', 'qtgsdetail')
                #url = urls['host']+'qtgsdetail/' + enttype+'/' + entpripid
                # sub_json_dict.update(self.crawl_other_dept_pub_pages(url))
                # # 司法协助公示信息 sfgsdetail
                #url = url.replace('qtgsdetail', 'sfgsdetail')
                #url = urls['host']+ 'sfgsdetail/' + enttype +'/' + entpripid
                # sub_json_dict.update(self.crawl_judical_assist_pub_pages(url))

        except Exception as e:
            settings.logger.error(u"An error ocurred when getting the main page, error: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #工商公式信息页面
    def crawl_ind_comm_pub_pages(self, url):
        sub_json_dict={}
        try:
            #url = "http://218.57.139.24/pub/gsgsdetail/1223/6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6"
            #page = html_from_file('next.html')
            page = self.crawl_page_by_url(url)['page']
            entpripid = url[url.rfind('/')+1:]
            post_data = {'encrpripid' : entpripid}

            """
            dj = self.parse_page(page, 'jibenxinxi') # class= result-table
            json_dump_to_file('shandong_json.json', dj)

            sub_json_dict['ind_comm_pub_reg_basic'] = {u'基本信息' : dj[u'基本信息'] if dj.has_key(u'基本信息') else []}        # 登记信息-基本信息
            sub_json_dict['ind_comm_pub_reg_shareholder'] = {u'股东信息': dj[u'股东信息'] if dj.has_key(u'股东信息') else [] }  # 股东信息
            sub_json_dict['ind_comm_pub_reg_modify'] = { u'变更信息' : dj[u'变更信息'] if dj.has_key(u'变更信息') else [] }      # 变更信息

            ba = self.parse_page(page, 'beian', post_data)
            json_dump_to_file('shandong_json.json', beian)

            sub_json_dict['ind_comm_pub_arch_key_persons'] = { u'主要人员信息' : ba[u'主要人员信息'] if ba.has_key(u'主要人员信息') else [] }  # 备案信息-主要人员信息
            sub_json_dict['ind_comm_pub_arch_branch'] = { u'分支机构信息' : ba[u'分支机构信息'] if ba.has_key(u'分支机构信息') else [] }      # 备案信息-分支机构信息
            sub_json_dict['ind_comm_pub_arch_liquidation'] = { u'清算信息': ba[u'清算信息'] if ba.has_key(u'清算信息') else [] }  # 备案信息-清算信息
            """
            titles = ('ind_comm_pub_movable_property_reg',  # 动产抵押登记信息
                     'ind_comm_pub_equity_ownership_reg',  # 股权出置登记信息
                     # 'ind_comm_pub_administration_sanction',  # 行政处罚信息
                     # 'ind_comm_pub_business_exception',  # 经营异常信息
                     # 'ind_comm_pub_serious_violate_law',  # 严重违法信息
                     # 'ind_comm_pub_spot_check'        # 抽查检查信息
                     )
            tabs = (
                        'dongchandiya',#动产抵押
                        'guquanchuzhi'  ,# 股权出质登记信息
                        # 'xingzhengchufa' ,#行政处罚
                        # 'jingyingyichangminglu' , # 企业经营异常
                        # 'yanzhongweifaqiye' , # 严重违法
                        # 'chouchaxinxi' ,#抽样检查
                    )
            for title, tab in zip(titles, tabs):
                sub_json_dict[title] = self.parse_page(page, tab, post_data)
            json_dump_to_file('shandong_json.json', sub_json_dict)
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ind_comm_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 企业公示信息 页面
    def crawl_ent_pub_pages(self, url):
        sub_json_dict = {}
        try:
            sub_json_dict['ent_pub_administration_license'] = []    #行政许可信息
            sub_json_dict['ent_pub_administration_sanction'] = []   #行政许可信息
            titles= (   'ent_pub_ent_annual_report',
                        'ent_pub_shareholder_capital_contribution', #企业投资人出资比例
                        'ent_pub_equity_change', #股权变更信息
                        'ent_pub_knowledge_property', #知识产权出资登记
                    )
            items = (
                        'nblist', #企业年报
                        'gdcz', #股东及出资
                        'gqbg', #股权变更信息
                        'zscq', #知识产权出质登记信息
                    )
            for title, item in zip(titles, items):
                page = self.crawl_page_by_url(url%item)['page']
                #html_to_file('shandong_dj.html', page)
                sub_json_dict[title] = self.parse_page(page)
        except Exception as e:
            logging.debug(u"An error ocurred in crawl_ent_pub_pages: %s"% type(e))
            raise e
        finally:
            return sub_json_dict
    #爬取 其他部门公示 页面
    def crawl_other_dept_pub_pages(self, url):
        sub_json_dict = {}
        try:
            titles =(   'other_dept_pub_administration_license',#行政许可信息
                        'other_dept_pub_administration_sanction'#行政处罚信息
                    )
            tabs=(  "gddjlist", # 股权冻结信息
                    "gdbglist", # 股东变更信息
                )
            for title, tab in zip(titles, tabs):
                page = self.crawl_page_by_url(url%tab)['page']
                sub_json_dict[title] = self.parse_page(page)
        except Exception as e:
            settings.logger.debug(u"An error ocurred in crawl_other_dept_pub_pages: %s"% (type(e)))
            raise e
        finally:
            return sub_json_dict
        pass

    def crawl_judical_assist_pub_pages(self, url):
        """爬取司法协助信息页面
        """
        pass


    def get_raw_text_by_tag(self, tag):
        return tag.get_text().strip()

    def get_table_title(self, table_tag):
        if table_tag.find('tr'):
            if table_tag.find('tr').find_all('th')  :
                if len(table_tag.find('tr').find_all('th')) > 1 :
                    return None
                # 处理 <th> aa<span> bb</span> </th>
                if table_tag.find('tr').th.stirng == None and len(table_tag.find('tr').th.contents) > 1:
                    # 处理 <th>   <span> bb</span> </th>  包含空格的
                    if (table_tag.find('tr').th.contents[0]).strip()  :
                        return (table_tag.find('tr').th.contents[0]).strip()
                # <th><span> bb</span> </th>
                return self.get_raw_text_by_tag(table_tag.find('tr').th)
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
        if bs4_tag.has_attr('href') and (bs4_tag['href'] != '#' and bs4_tag['href'] != 'javascript:void(0);'):
            #print 'href'
            pattern = re.compile(r'http'| r'javascript:void(0);')
            if pattern.search(bs4_tag['href']):
                return bs4_tag['href']
            return urls['prefix_url'] + bs4_tag['href']
        elif bs4_tag.has_attr('onclick'):
            #print 'onclick'
            txt= bs4_tag['onclick']
            if re.compile('CheckDetail').search(txt):

                re1='.*?'   # Non-greedy match on filler
                re2='(?:[a-z][a-z]+)'   # Uninteresting: word
                re3='.*?'   # Non-greedy match on filler
                re4='((?:[a-z][a-z]+))' # Word 1

                rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
                m = rg.search(txt)
                if m:
                    key=m.group(1)
                    re1='.*?'   # Non-greedy match on filler
                    re2='(\\\'.*?\\\')' # Single Quote String 1
                    re3='.*?'   # Non-greedy match on filler
                    re4='(\\\'.*?\\\')' # Single Quote String 2

                    rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
                    m = rg.search(txt)
                    if m:
                        # strip extra \'\' for each side
                        id_str=m.group(1)[1:-1]
                        entid_str=m.group(2)[1:-1]
                    url = urls['host'] + CheckDetail[key]%(id_str, entid_str)

            elif re.compile('nbdetail').search(txt):
                re1='.*?'   # Non-greedy match on filler
                re2='(\\\'.*?\\\')' # Single Quote String 1
                re3='.*?'   # Non-greedy match on filler
                re4='(\\\'.*?\\\')' # Single Quote String 2

                rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
                m = rg.search(txt)
                if m:
                    entid_str=m.group(1)[1:-1]
                    year_str=m.group(2)[1:-1]
                url = urls['host'] + "/report/annals?entid=%s&year=%s&hasInfo=0"%(entid_str, year_str)
            elif re.compile('sfGddjDetail').search(txt):
                re1='.*?'   # Non-greedy match on filler
                re2='(\\\'.*?\\\')' # Single Quote String 1
                re3='.*?'   # Non-greedy match on filler
                re4='(\\\'.*?\\\')' # Single Quote String 2

                rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
                m = rg.search(txt)
                if m:
                    id_str=m.group(1)[1:-1]
                    entid_str=m.group(2)[1:-1]
                url = urls['host'] + "/report/gddjdetail?id=%s&entid=%s&hasInfo=0"%(id_str, entid_str)
            return url
        return None


    def get_columns_of_record_table(self, bs_table, page, table_name):
        tbody = None
        if len(bs_table.find_all('tbody')) > 1:
            tbody= bs_table.find_all('tbody')[0]
        else:
            tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')

        tr = None
        print tbody
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
        ret_val=  self.get_record_table_columns_by_tr(tr, table_name)
        #settings.logger.debug(u"ret_val->%s\n", ret_val)
        return  ret_val

    def get_record_table_columns_by_tr(self, tr_tag, table_name):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            if len(tr_tag.find_all('th'))==0 :
                logging.error(u"The table %s has no columns"% table_name)
                return columns
            count = 0
            if len(tr_tag.find_all('th'))>0 :
                for th in tr_tag.find_all('th'):
                    #logging.debug(u"th in get_record_table_columns_by_tr =\n %s", th)
                    col_name = self.get_raw_text_by_tag(th)
                    if col_name :
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
            logging.error(u'exception occured in get_table_columns, except_type = %s, table_name = %s' % (type(e), table_name))
        finally:
            return columns

    # 分析企业年报详细页面
    def parse_ent_pub_annual_report_page(self, page):
        sub_dict = {}
        try:
            soup = BeautifulSoup(page, 'html5lib')
            # 基本信息表包含两个表头, 需要单独处理
            basic_table = soup.find('table')
            trs = basic_table.find_all('tr')
            title = self.get_raw_text_by_tag(trs[1].th)
            table_dict = {}
            for tr in trs[2:]:
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
            sub_dict[title] = table_dict
            content_table = soup.find_all('table')[1:]
            for table in content_table:
                table_name = self.get_table_title(table)
                table_data = self.parse_table(table, table_name, page)
                sub_dict[table_name] = table_data
        except Exception as e:
            settings.logger.error(u'annual page: fail to get table data with exception %s' % e)
            raise e
        finally:
            return sub_dict

    # parse main page
    # return params are dicts

    dicts={
        u"主要人员信息" : "http://218.57.139.24/pub/gsryxx/1223",
        u"分支机构信息" : "http://218.57.139.24/pub/gsfzjg/1223",
        u"动产抵押登记信息": "http://218.57.139.24/pub/gsdcdy",
        u"股权出质登记信息":"http://218.57.139.24/pub/gsgqcz",
    }

    def parse_page(self, page, div_id, post_data= {}):
        soup = BeautifulSoup(page, 'html5lib')
        page_data = {}

        try:
            div = soup.find('div', attrs = {'id':div_id})
            if div:
                table = div.find('table')
            else:
                table = soup.find('table')
            #print table
            while table:
                if table.name == 'table':
                    table_name = self.get_table_title(table)
                    if table_name:
                        if table_name == u"股东信息":
                            page_data[table_name] =  self.parse_table_gudong(table, table_name, page)
                        elif table_name == u"变更信息":
                            page_data[table_name] = self.parse_table_biangeng(table, table_name, page)
                        elif table_name == u"股东及出资信息":
                            page_data[table_name] = self.parse_table_gdczxx(table, table_name, page)
                        elif table_name == u"主要人员信息":
                            page_data[table_name] = self.parse_table_people(table, table_name, page, post_data)
                        elif table_name == u"分支机构信息":
                            page_data[table_name] = self.parse_table_branch(table, table_name, page, post_data)
                        elif table_name == u"动产抵押登记信息":
                            page_data[table_name] = self.parse_table_dongchandiya(table, table_name, page, post_data)
                        elif table_name == u"股权出质登记信息":
                            page_data[table_name] = self.parse_table_guquanchuzhi(table, table_name, page, post_data)


                        else:
                            page_data[table_name] = self.parse_table(table, table_name, page)
                table = table.nextSibling

        except Exception as e:
            logging.error(u'parse failed, with exception %s' % e)
            raise e
        finally:
            return page_data
    # 股权出质
    def parse_table_guquanchuzhi(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name]
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_dict = l['equpledate']
                link = urls['webroot']+"pub/gsgqczdetail/"+post_data['encrpripid']+"/"+str(l['equityno'])+"/"+str(l['type'])
                print link
                link_page = self.crawl_page_by_url(link)['page']
                print link_page
                link_data = self.parse_page(link_page)
                print link_data
                datas = [i+1, l['equityno'], l['pledgor'], l['blicno'], l['impam']+l['pledamunit'], l['imporg'], l['impmorblicno'], str(date_dict['year']+1900)+'年'+ str(date_dict['month']%12+1)+'月'+ str(date_dict['date'])+'日' ,'有效' if l['type']==1 else '无效', link_data]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            settings.logger.error(u"parse table 股权出质 failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 动产抵押登记信息
    def parse_table_dongchandiya(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name] #"http://218.57.139.24/pub/gsfzjg/1223"
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                date_dict = l['regidate']
                # 详情处没有处理，还没有见到有数据的表格
                datas = [i+1, l['morregcno'], str(date_dict['year']+1900)+'年'+ str(date_dict['month']%12+1)+'月'+ str(date_dict['date'])+'日' ,l['regorg'], str(l['priclasecam'])+"万元", '有效' if l['type']==1 else '无效', '详情']
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            settings.logger.error(u"parse table dongchandiya failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 分支机构信息
    def parse_table_branch(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name] #"http://218.57.139.24/pub/gsfzjg/1223"
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            #print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                datas = [i+1, l['name'], l['position']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            settings.logger.error(u"parse table branch failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 主要人员信息
    def parse_table_people(self, bs_table, table_name, page, post_data):
        sub_json_list=[]
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            url = self.dicts[table_name] #"http://218.57.139.24/pub/gsryxx/1223"
            #print post_data
            res = self.crawl_page_by_url_post(url, post_data, {'X-CSRF-TOKEN': self.csrf})['page']
            print type(res)
            ls = json.loads(res)
            for i, l in enumerate(ls):
                datas = [i+1, l['regno'], l['brname'], l['regorg']]
                sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            settings.logger.error(u"parse table main people failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    # 股东信息表
    def parse_table_gudong(self, bs_table, table_name, page):
        sub_json_list = []
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]
            #czxxlist
            m = re.compile(r"czxxliststr =(\'.*?\')").search(page)
            if m:
                czxxliststr = m.group(1)
                czxxlist = eval(re.compile(r"(\'.*?\')").search(czxxliststr).group(1)[1:-1])  # 将字符串转换成list
                #print type(czxxlist)
                #var encrpripid = '6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6';
                m1  = re.compile(r"encrpripid = (\'.*?\')").search(page)
                if m1:
                    pripidstr = m1.group(1)

                    encrpripid = re.compile(r"(\'.*?\')").search(pripidstr).group(1)[1:-1]

                    for item in czxxlist:
                        if item['xzqh'] == "1":
                            link = urls['webroot'] + 'pub/gsnzczxxdetail/'+ encrpripid+'/'+ item['recid']
                            link_page = self.crawl_page_by_url(link)['page']
                            link_data = self.parse_page(link_page, table_name+'_detail')
                            datas = [ item['invtype'], item['inv'], item['blictype'], item['blicno'], link_data]
                        else:
                            datas = [ item['invtype'], item['inv'], item['blictype'], item['blicno'], '']
                        sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            settings.logger.error(u"parse table gudong failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list
    # 股东及出资信息
    def parse_table_gdczxx(self, bs_table, table_name, page):
        sub_json_dict= {}
        try:
            #columns = self.get_columns_of_record_table(bs_table, page, table_name)
            #czxxlist
            m = re.compile(r"czxxstr =(\'.*?\')").search(page)
            if m:
                czxxliststr = m.group(1)
                czxxlist = eval(re.compile(r"(\'.*?\')").search(czxxliststr).group(1)[1:-1])  # 将字符串转换成list
                m1  = re.compile(r"czxxrjstr =(\'.*?\')").search(page)      # 认缴
                if m1:
                    czxxrjstr = m1.group(1)
                    czxxrjlist = eval(re.compile(r"(\'.*?\')").search(czxxrjstr).group(1)[1:-1])
                    m2  = re.compile(r"czxxsjstr =(\'.*?\')").search(page)      # 实缴
                    if m2:
                        czxxsjstr = m2.group(1)
                        czxxsjlist = eval(re.compile(r"(\'.*?\')").search(czxxsjstr).group(1)[1:-1])

                        ######################
                        item = {}
                        sub_item = {}
                        item[u'股东（发起人）'] = czxxlist[0]['inv']
                        item[u'认缴额（万元）'] = czxxlist[0]['lisubconam']
                        item[u'实缴额（万元）'] = czxxlist[0]['liacconam']
                        if len(czxxrjlist) >0 :
                            sub_item[u'认缴出资方式'] =  czxxrjlist[0]['conform']
                            sub_item[u'认缴出资额（万元）'] =czxxrjlist[0]['subconam']
                            date_dict = czxxsjlist[0]['condate']
                            #print type(date_dict['date'])   全是int型
                            sub_item[u'认缴出资日期'] =str(date_dict['year']+1900)+'年'+ str(date_dict['month']%12+1)+'月'+ str(date_dict['date'])+'日'
                            item[u'认缴明细'] = sub_item
                        if len(czxxsjlist) > 0 :
                            sub_item = {}
                            sub_item[u'实缴出资方式'] =czxxsjlist[0]['conform']
                            sub_item[u'实缴出资额（万元）'] =czxxsjlist[0]['acconam']
                            date_dict = czxxsjlist[0]['condate']

                            sub_item[u'实缴出资日期'] = str(date_dict['year']+1900)+'年'+ str(date_dict['month']%12+1)+'月'+ str(date_dict['date'])+'日'
                            item[u'实缴明细'] = sub_item
                        sub_json_dict = (item.copy())
        except Exception as e:
            settings.logger.error(u"parse table gudongczxx failed with exception:%s" % (type(e)))
        finally:
            return sub_json_dict
        pass
    # 变更信息表
    def parse_table_biangeng(self, bs_table, table_name, page):
        sub_json_list = []
        try:
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            titles = [column[0] for column in columns]

            m = re.compile(r"bgsxliststr =(\'.*?\')").search(page)
            if m:
                bgsxliststr = m.group(1)
                bgsxlist = eval(re.compile(r"(\'.*?\')").search(bgsxliststr).group(1)[1:-1])  # 将字符串转换成list
                #print type(bgsxlist)
                for item in bgsxlist:
                    date_dict = item['altdate']
                    datas = [ item['altitem'], item['altbe'], item['altaf'], str(date_dict['year']+1900)+'年'+ str(date_dict['month']%12+1)+'月'+ str(date_dict['date'])+'日']
                    sub_json_list.append(dict(zip(titles, datas)))
        except Exception as e:
            settings.logger.error(u"parse table gudong failed with exception:%s" % (type(e)))
        finally:
            return sub_json_list

    def parse_table(self, bs_table, table_name, page):
        table_dict = None
        try:
            # tb_title = self.get_table_title(bs_table)
            #this is a fucking dog case, we can't find tbody-tag in table-tag, but we can see tbody-tag in table-tag
            #in case of that, we use the whole html page to locate the tbody
            print table_name
            columns = self.get_columns_of_record_table(bs_table, page, table_name)
            #print columns
            tbody = None
            if len(bs_table.find_all('tbody'))>1:
                tbody = bs_table.find_all('tbody')[1]
            else:
                tbody = bs_table.find('tbody') or BeautifulSoup(page, 'html5lib').find('tbody')
            if columns:
                col_span = 0
                single_col = 0
                for col in columns:
                    if type(col[1]) == list:
                        col_span += len(col[1])
                    else:
                        single_col+=1
                        col_span += 1

                column_size = len(columns)
                item_array = []
                if not tbody:
                    records_tag = bs_table
                else:
                    records_tag = tbody
                item = None

                for tr in records_tag.find_all('tr'):
                    if tr.find_all('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'))
                                #print 'next_url: ' + next_url
                                if next_url:
                                    detail_page = self.crawl_page_by_url(next_url)
                                    #html_to_file("next.html", detail_page['page'])
                                    #print "table_name : "+ table_name
                                    if table_name == u'年报信息':
                                        #logging.debug(u"next_url = %s, table_name= %s\n", detail_page['url'], table_name)
                                        page_data = self.parse_ent_pub_annual_report_page(detail_page['page'])

                                        item[columns[col_count][0]] = page_data #this may be a detail page data
                                    else:
                                        page_data = self.parse_page(detail_page['page'])
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
                    elif tr.find_all('td') and len(tr.find_all('td', recursive=False)) == col_span and col_span != column_size:
                        col_count = 0
                        sub_col_index = 0
                        item = {}
                        sub_item = {}
                        for td in tr.find_all('td',recursive=False):
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


    def crawl_page_by_url(self, url):
        r = self.requests.get( url)
        if r.status_code != 200:
            settings.logger.error(u"Getting page by url:%s\n, return status %s\n"% (url, r.status_code))
            return False
        # 为了防止页面间接跳转，获取最终目标url
        return {'page' : r.text, 'url': r.url}

    def crawl_page_by_url_post(self, url, data, headers={}):
        if headers:
            self.requests.headers.update(headers)
            r = self.requests.post(url, data)
        else :
            r = self.requests.post(url, data)
        if r.status_code != 200:
            settings.logger.error(u"Getting page by url with post:%s\n, return status %s\n"% (url, r.status_code))
            return False
        return {'page': r.text, 'url': r.url}

    def run(self, ent_num):
        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        self.json_dict = {}
        self.crawl_page_search(urls['page_search'])
        self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        self.json_dict[ent_num] = data
        json_dump_to_file(self.json_restore_path , self.json_dict)

    def work(self, ent_num= ""):

        if not os.path.exists(self.html_restore_path):
            os.makedirs(self.html_restore_path)
        # self.json_dict = {}

        self.crawl_page_search(urls['page_search'])
        self.crawl_page_captcha(urls['page_Captcha'], urls['checkcode'], urls['page_showinfo'], ent_num)
        data = self.crawl_page_main()
        #url = "http://218.57.139.24/pub/gsgsdetail/1223/6e0948678bfeed4ac8115d5cafef819ad6951a24f0c0188cd6c047570329c9b6"
        #data = self.crawl_ind_comm_pub_pages(url)
        #self.ents= ['/platform/saic/viewBase.ftl?entId=349DDA405D520231E04400306EF52828']
        #data = self.crawl_page_main()

        #txt = html_from_file('shandong_dj.html')
        #txt = html_from_file('next.html')
        #data = self.parse_page(txt)
        #data = self.parse_ent_pub_annual_report_page(txt)
        #data = self.parse_page(txt)
        #json_dump_to_file('shandong_json.json', data)


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

def html_from_file(path):
    if not os.path.exists(path):
        return
    a = ""
    with codecs.open(path, 'r') as f:
        a = f.read()
    return a

def read_ent_from_file(path):
    read_type = 'r'
    if not os.path.exists(path):
        settings.logger.error(u"There is no path : %s"% path )
    lines = []
    with codecs.open(path, read_type, 'utf-8') as f:
        lines = f.readlines()
    lines = [ line.split(',') for line in lines ]
    return lines

if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    shandong = ShandongCrawler('./enterprise_crawler/shandong.json')
    shandong.work('370000018067809')
    #shandong.work('120000000000165')

"""
if __name__ == "__main__":
    reload (sys)
    sys.setdefaultencoding('utf8')
    import run
    run.config_logging()
    if not os.path.exists("./enterprise_crawler"):
        os.makedirs("./enterprise_crawler")
    shandong = ShandongCrawler('./enterprise_crawler/shandong.json')
    ents = read_ent_from_file("./enterprise_list/shandong.txt")
    shandong = ShandongCrawler('./enterprise_crawler/shandong.json')
    for ent_str in ents:
        settings.logger.info(u'###################   Start to crawl enterprise with id %s   ###################\n' % ent_str[2])
        shandong.run(ent_num = ent_str[2])
        settings.logger.info(u'###################   Enterprise with id  %s Finished!  ###################\n' % ent_str[2])
"""

