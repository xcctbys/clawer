#!/usr/bin/env python
#encoding=utf-8
import os
import time
import threading
import re
import json
import errno
import urllib
import urllib2
import cookielib
import logging
import codecs
import CaptchaRecognition as CR
import bs4
class CrawlerUtils(object):
    @staticmethod
    def make_dir(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    @staticmethod
    def set_logging(level):
        logging.basicConfig(level = level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")

    @staticmethod
    def set_opener_header(opener, header):
        tmp_header = []
        opener.addheaders = []
        for key, value in header.items():
            elem = (key, value)
            tmp_header.append(elem)
        opener.addheaders = tmp_header

    @staticmethod
    def add_opener_header(opener, header):
        for key, value in header.items():
            elem = (key, value)
            opener.addheaders.append(elem)

    @staticmethod
    def make_opener(head = {
                'Connetion': 'Keep-Alive',
                'Accept': 'text/html, application/xhtml+xml, */*',
                'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'}):

        cj = cookielib.CookieJar()
        pro = urllib2.HTTPCookieProcessor(cj) #Python自动处理cookie
        opener = urllib2.build_opener(pro)    #用于打开url的opener
        urllib2.install_opener(opener)
        CrawlerUtils.set_opener_header(opener, head)
        return opener

    #在给定的url基础上，添加额外的信息
    @staticmethod
    def add_params_to_url(url, args):
        return url + urllib.urlencode(args)

    @staticmethod
    def save_page_to_file(path, page):
        with open(path, 'w') as f:
            f.write(page)

    @staticmethod
    def get_enterprise_list(file):
        list = []
        with open(file, 'r') as f:
            for line in f.readlines():
                sp = line.split(',')
                if len(sp) >= 3:
                    list.append(sp[2].strip(' \n\r'))
        return list

    @staticmethod
    def display_item(item):
        if type(item) == list or type(item) == tuple:
            for i in item:
                CrawlerUtils.display_item(i)
        elif type(item) == dict:
            for k in item:
                CrawlerUtils.display_item(k)
                CrawlerUtils.display_item(item[k])
        elif type(item) in (int, str, float, bool, bs4.element.NavigableString):
            print item
        elif type(item) == unicode:
            print item.encode('utf-8')
        else:
            print 'unknown type in CrawlerUtils.display_item, type = %s' % type(item)

    @staticmethod
    def json_dump_to_file(path, json_dict):
        write_type = 'w'
        if os.path.exists(path):
            write_type = 'a'
        with codecs.open(path, write_type, 'utf-8') as f:
            f.write(json.dumps(json_dict, ensure_ascii=False)+'\n')

    @staticmethod
    def get_raw_text_in_bstag(tag):
        text = tag.string
        if not text:
            text = tag.get_text()
        if not text:
            return ''
        return text.strip()

    @staticmethod
    def get_cur_time():
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

    @staticmethod
    def get_cur_date():
        return time.strftime("%Y-%m-%d",time.localtime(time.time()))

class CheckCodeCracker(object):
    def __init__(self):
        self.cr = CR.CaptchaRecognition()

    def crack(self, ckcode_image_path):
        return self.cr.predict_result(ckcode_image_path)


class Crawler(object):
    html_restore_path = './'
    json_restore_path = './'
    #create mutex lock (on write json object to file)
    write_file_mutex = threading.Lock()

    def __init__(self, ck_cracker):
        self.ck_cracker = ck_cracker
        self.ckcode_image_path = self.json_restore_path + 'ckcode.jpg'
        self.crawl_time = CrawlerUtils.get_cur_date()
        print self.ckcode_image_path

    def crawl_work(self, ent_number = 0):
        self.ent_number = str(ent_number)
        self.ent_id = ''
        self.html_restore_path = self.__class__.html_restore_path + self.ent_number + '/'
        self.json_restore_path = self.__class__.json_restore_path

        if not os.path.exists(self.html_restore_path):
            CrawlerUtils.make_dir(self.html_restore_path)

        if not os.path.exists(self.json_restore_path):
            CrawlerUtils.make_dir(self.json_restore_path)

        self.json_dict = {}
        self.opener = CrawlerUtils.make_opener()
        self.crawl_check_page()
        self.crawl_ind_comm_pub_pages()
        self.crawl_ent_pub_pages()
        self.crawl_other_dept_pub_pages()

        #use multi-thread to crawl, when we write data to our single file, use mutex lock
        self.write_file_mutex.acquire()
        CrawlerUtils.json_dump_to_file(self.json_restore_path + self.crawl_time + '.json', {self.ent_number : self.json_dict})
        self.write_file_mutex.release()

    def crack_checkcode(self):
        checkcode_url =  self.get_checkcode_url()
        page = self.opener.open(checkcode_url).read()
        time.sleep(1)
        with open(self.ckcode_image_path, 'w') as f:
            f.write(page)
        return self.ck_cracker.crack(self.ckcode_image_path)

    def crawl_check_page(self):
        pass

    def crawl_ind_comm_pub_pages(self):
        pass

    def crawl_ent_pub_pages(self):
        pass

    def crawl_other_dept_pub_pages(self):
        pass

    def crawl_judical_assist_pub_pages(self):
        pass
