#!/usr/bin/env python
#encoding=utf-8

import os
import sys
import re
import unittest
import settings
import logging
from bs4 import BeautifulSoup
from hparser import Parser
from crawler import CrawlerUtils
from crawler import CheckCodeCracker
from beijing_crawler import CrawlerBeijingEnt

class ParserBeijingEnt(Parser):
    def __init__(self, crawler):
        super(self.__class__, self).__init__()
        self.crawler = crawler

    def parse_page(self, page, type):
        soup = BeautifulSoup(page)
        page_data = {}
        if soup.body:
            if soup.body.table:
                try:
                    #if one page only has a table, just use the table data as dict_meta
                    if len(soup.body.find_all('table')) == 1:
                        if type == 'ind_comm_pub_reg_modify':
                            page_data = self.parse_ind_comm_pub_reg_modify_table(soup.body.table, type, page)
                        else:
                            page_data = self.parse_table(soup.body.table, type, page)

                    #if one page has more than one table, dict_meta should contain data of all table
                    else:
                        table = soup.body.find('table')
                        while table:
                            if table.name == 'table':
                                table_name = self.get_table_title(table)
                                page_data[table_name] = self.parse_table(table, table_name, page)
                            table = table.nextSibling
                except Exception as e:
                    logging.error('parse failed, with exception %s' % e)
                finally:
                    pass
        return page_data

    #get column data recursively, use recursive because there may be table in table
    def get_column_data(self, columns, td_tag):
        if type(columns) == list:
            data = {}
            multi_col_tag = td_tag
            if td_tag.find('table'):
                multi_col_tag = td_tag.find('table').find('tr')
            if not multi_col_tag:
                logging.deubg('invalid multi_col_tag, multi_col_tag = %s', multi_col_tag)
                return data

            if len(columns) != len(multi_col_tag.find_all('td', recursive=False)):
                logging.debug('column head size != column data size, columns head = %s, columns data = %s' % (columns, multi_col_tag.contents))
                return data

            for id, col in enumerate(columns):
                data[col[0]] = self.get_column_data(col[1], multi_col_tag.find_all('td', recursive=False)[id])
            return data
        else:
            return CrawlerUtils.get_raw_text_in_bstag(td_tag)

    def get_columns_of_record_table(self, bs_table, page):
        tbody = bs_table.find('tbody') or BeautifulSoup(page).find('tbody')
        tr = None
        if tbody:
            if len(tbody.find_all('tr')) <= 1:
                tr = tbody.find('tr')
            else:
                tr = tbody.find_all('tr')[1]
                if not tr.find('th'):
                    tr = tbody.find_all('tr')[0]
        else:
            if len(bs_table.find_all('tr')) <= 1:
                return None
            elif bs_table.find_all('tr')[0].find('th') and not bs_table.find_all('tr')[0].find('td') and len(bs_table.find_all('tr')[0].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[0]
            elif bs_table.find_all('tr')[1].find('th') and not bs_table.find_all('tr')[1].find('td') and len(bs_table.find_all('tr')[1].find_all('th')) > 1:
                tr = bs_table.find_all('tr')[1]
        return self.get_record_table_columns_by_tr(tr)

    def sub_column_count(self, th_tag):
        if th_tag.has_attr('colspan') and th_tag.get('colspan') > 1:
            return int(th_tag.get('colspan'))
        return 0

    def get_sub_columns(self, tr_tag, index, count):
        columns = []
        for i in range(index, index + count):
            th = tr_tag.find_all('th')[i]
            if not self.sub_column_count(th):
                columns.append((CrawlerUtils.get_raw_text_in_bstag(th), CrawlerUtils.get_raw_text_in_bstag(th)))
            else:
            #if has sub-sub columns
                columns.append((CrawlerUtils.get_raw_text_in_bstag(th), self.get_sub_columns(tr_tag.nextSibling.nextSibling, 0, self.sub_column_count(th))))
        return columns

    def get_record_table_columns_by_tr(self, tr_tag):
        columns = []
        if not tr_tag:
            return columns
        try:
            sub_col_index = 0
            for th in tr_tag:
                col_name = CrawlerUtils.get_raw_text_in_bstag(th)
                if col_name and col_name not in columns:
                    if not self.sub_column_count(th):
                        columns.append((col_name, col_name))
                    else: #has sub_columns
                        columns.append((col_name, self.get_sub_columns(tr_tag.nextSibling.nextSibling, sub_col_index, self.sub_column_count(th))))
                        sub_col_index += self.sub_column_count(th)
        except Exception as e:
            logging.error('exception occured in get_table_columns, except_type = %s' % type(e))
        finally:
            return columns


    def parse_table(self, bs_table, table_name, page):
        table_dict = None
        try:
            # tb_title = self.get_table_title(bs_table)
            #this is a fucking dog case, we can't find tbody-tag in table-tag, but we can see tbody-tag in table-tag
            #in case of that, we use the whole html page to locate the tbody

            columns = self.get_columns_of_record_table(bs_table, page)

            tbody = bs_table.find('tbody') or BeautifulSoup(page).find('tbody')
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
                    if tr.find('td') and len(tr.find_all('td', recursive=False)) % column_size == 0:
                        col_count = 0
                        item = {}
                        for td in tr.find_all('td',recursive=False):
                            if td.find('a'):
                                #try to retrieve detail link from page
                                next_url = self.get_detail_link(td.find('a'), page)
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)

                                    if table_name == 'ent_pub_ent_annual_report':
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
                                next_url = self.get_detail_link(td.find('a'), page)
                                #has detail link
                                if next_url:
                                    detail_page = self.crawler.crawl_page_by_url(next_url)

                                    if table_name == 'ent_pub_ent_annual_report':
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
                                    sub_item[sub_key] = CrawlerUtils.get_raw_text_in_bstag(td)
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
                            logging.debug('th size not equals td size in table %s, what\'s up??' % table_name)
                            return
                        else:
                            for i in range(len(ths)):
                                if CrawlerUtils.get_raw_text_in_bstag(ths[i]):
                                    table_dict[CrawlerUtils.get_raw_text_in_bstag(ths[i])] = CrawlerUtils.get_raw_text_in_bstag(tds[i])
        except Exception as e:
            logging.error('parse table %s failed with exception %s' % (table_name, type(e)))
        finally:
            return table_dict

    def parse_ent_pub_annual_report_page(self, base_page, page_type):
        def get_year_of_annual_report(page):
            soup = BeautifulSoup(page)
            t = soup.body.find('table')
            return CrawlerUtils.get_raw_text_in_bstag(t.find('tr'))

        if settings.save_html:
            CrawlerUtils.save_page_to_file(self.crawler.html_restore_path + 'annual_report_base_info.html', base_page)

        page_data = {}
        soup = BeautifulSoup(base_page)
        if soup.body.find('table'):
            base_table = soup.body.find('table')
            table_name = u'企业基本信息'#self.get_table_title(base_table)
            page_data[table_name] = self.parse_table(base_table, table_name, base_page)

            if len(soup.find_all('table')) > 1:
                ent_property_table = soup.body.find_all('table')[1]
                table_name = self.get_table_title(ent_property_table)
                page_data[table_name] = self.parse_table(ent_property_table, table_name, base_page)
        else:
            pass

        year = get_year_of_annual_report(base_page)
        report_items = {'wzFrame' : 'website_info', 'gdczFrame':'shareholder_contribute_info', 'dwdbFrame' : 'external_guarantee_info', 'xgFrame':'modify_record_info'}
        for item in report_items.items():
            pat = re.compile(r'<iframe +id="%s" +src=\'(/entPub/entPubAction!.+)\'' % item[0])
            m = pat.search(base_page)
            if m:
                next_url = CrawlerBeijingEnt.urls['host'] + m.group(1)
                logging.info('get annual report, url:\n%s\n' % next_url)
                page = self.crawler.crawl_page_by_url(next_url)
                pages = self.crawler.get_all_pages_of_a_section(page, page_type)

                table_name = item[1]
                try:
                    soup = BeautifulSoup(page)
                    table_name = self.get_table_title(soup.body.table)
                except Exception as e:
                    logging.error('fail to get table name with exception %s' % e)

                try:
                    if len(pages) == 1:
                        table_data = self.parse_page(page, table_name)
                    else:
                        table_data = []
                        for p in pages:
                            table_data += self.parse_page(p, table_name)
                except Exception as e:
                    logging.error('fail to parse page with exception %s'%e)
                finally:
                    page_data[table_name] = table_data
        return page_data

    #parse the ind_comm_pub_reg_modify table
    def parse_ind_comm_pub_reg_modify_table(self, bs_table, table_name, page):
        tbody = bs_table.find('tbody')
        if tbody:
            columns = self.get_columns_of_record_table(bs_table, page)
            column_size = len(columns)
            item_array = []

            for tr in tbody.find_all('tr'):
                if tr.find('td'):
                    col_count = 0
                    item = {}
                    for td in tr.find_all('td'):
                        if td.find('a'):
                            #try to retrieve detail link from page
                            next_url = self.get_detail_link(td.find('a'), page)
                            #has detail link
                            if next_url:
                                detail_page = self.crawler.crawl_page_by_url(next_url)
                                detail_soup = BeautifulSoup(detail_page)
                                before_modify_table = detail_soup.body.find_all('table')[1]
                                table_data = self.parse_table(before_modify_table, 'before_modify', detail_page)
                                item[columns[col_count][0]] = self.parse_table(before_modify_table, 'before_modify', detail_page)
                                col_count += 1
                                after_modify_table = detail_soup.body.find_all('table')[2]
                                item[columns[col_count][0]] = self.parse_table(after_modify_table, 'after_modify', detail_page)
                            else:
                                item[columns[col_count][0]] = CrawlerUtils.get_raw_text_in_bstag(td)
                        else:
                            item[columns[col_count][0]] = CrawlerUtils.get_raw_text_in_bstag(td)

                        col_count += 1
                        if col_count == column_size:
                            item_array.append(item.copy())
                            col_count = 0
            return item_array

    def get_table_title(self, table_tag):
        if table_tag.find('tr'):
            return CrawlerUtils.get_raw_text_in_bstag(table_tag.find('tr').th)
        return ''

    def get_detail_link(self, bs4_tag, page):
        detail_op = bs4_tag.get('onclick')
        pat_view_info = re.compile(r'viewInfo\(\'([\w]+)\'\)')
        pat_show_dialog = re.compile(r'showDialog\(\'([^\'\n]+)\'')
        next_url = ''
        if detail_op and pat_view_info.search(detail_op):
            m = pat_view_info.search(detail_op)
            val = m.group(1)
            #detail link type 1, for example : ind_comm_pub info --- registration info -- shareholders info
            pat = re.compile(r'var +url += +rootPath +\+ +\"(.+\?)([\w]+)=\"\+[\w]+\+\"')
            m1 = pat.search(page)
            if m1:
                addition_url = m1.group(1)
                query_key = m1.group(2)

                next_url = CrawlerUtils.add_params_to_url(CrawlerBeijingEnt.urls['host'] + addition_url,
                                                          {query_key:val,
                                                          'entId':self.crawler.ent_id,
                                                            'ent_id':self.crawler.ent_id,
                                                            'entid':self.crawler.ent_id,
                                                            'credit_ticket':self.crawler.credit_ticket,
                                                            'entNo':self.crawler.ent_number
                                            })
        elif detail_op and pat_show_dialog.search(detail_op):
            #detail link type 2, for example : ind_comm_pub_info --- registration info ---- modify info
            m = pat_show_dialog.search(detail_op)
            val = m.group(1)
            next_url = CrawlerBeijingEnt.urls['host'] + val
        elif 'href' in bs4_tag.attrs.keys():
            #detail link type 3, for example : ent pub info ----- enterprise annual report
            next_url = CrawlerBeijingEnt.urls['host'] + bs4_tag['href']

        return next_url


class TestParser(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.parser = ParserBeijingEnt(CrawlerBeijingEnt(CheckCodeCracker()))
    #
    # def test_get_table_title(self):
    #     soup = BeautifulSoup(self.page)
    #     bs4_tag = soup.find_all('table')[0]
    #     print self.parser.get_table_title(bs4_tag)
    #
    # def test_parse_table(self):
    #     soup = BeautifulSoup(self.page)
    #     bs_table = soup.find_all('table')[0]
    #     table_dict = {}
    #     self.parser.parse_table(bs_table, 'reg_basic_info', table_dict)
    #     table_dict = table_dict['reg_basic_info']
    #     CrawlerUtils.display_item(table_dict)
    #
    # def test_parse_page(self):
    #     with open('./unittest_data/htmls/ind_comm_pub_reg_shareholder.html', 'r') as f:
    #         self.page = ''
    #         for l in f.readlines():
    #             self.page += l
    #
    #     page_data = self.parser.parse_page(self.page, 'ind_comm_pub_reg_shareholder')
    #     import json
    #     import codecs
    #     print json.dumps(page_data, ensure_ascii=False)
    #
    #     with codecs.open('./1.json', 'w', 'utf-8') as f:
    #         f.write(json.dumps(page_data, ensure_ascii=False))
    #
    #
    # def test_write_json(self):
    #     import json
    #     json_dict = {'hello':"好人", 1:200}
    #     print json.dumps(json_dict, ensure_ascii=False)
    #     with open('./1.json', 'w') as f:
    #         f.write(json.dumps(json_dict, ensure_ascii=False))

    # def test_parse_modify_detail_table(self):
    #     detail_page = ''
    #     with open('./unittest_data/htmls/detail.html', 'r') as f:
    #         for l in f.readlines():
    #             detail_page += l
    #     detail_soup = BeautifulSoup(detail_page)
    #     before_modify_table = detail_soup.body.find_all('table')[1]
    #     print before_modify_table
    #     table_data = self.parser.parse_table(before_modify_table, 'before_modify', detail_page)
    #     print table_data

    def test_parse_sub_columns_table_case(self):
        page = ''
        with open('./unittest_data/htmls/ind_comm_pub_reg_modify.html', 'r') as f:
            for l in f.readlines():
                page += l
        soup = BeautifulSoup(page)
        bs_table = soup.body.find('table')
        cols = self.parser.get_columns_of_record_table(bs_table, page)

        table_data = self.parser.parse_page(page, 'reg_modify')

        import json
        import codecs
        print json.dumps(table_data, ensure_ascii=False)
        with codecs.open('./1.json', 'w', 'utf-8') as f:
            f.write(json.dumps(table_data, ensure_ascii=False))




if __name__ == '__main__':
    CrawlerUtils.set_logging(settings.log_level)
    unittest.main()
    pass