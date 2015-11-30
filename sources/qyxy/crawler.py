#!/usr/bin/env python
#encoding=utf-8
import os
import re
import errno
import urllib
import urllib2
import cookielib
import logging
import CaptchaRecognition as CR

class CrawlerUtils(object):
    @staticmethod
    def make_dir(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    @staticmethod
    def set_logging(debug):
        if debug:
            level = logging.DEBUG
        else:
            level = logging.ERROR
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
                list.append(sp[2])
        return list

class CheckCodeCracker(object):
    def __init__(self):
        self.cr = CR.CaptchaRecognition()

    def crack(self, ckcode_image_path):
        return self.cr.predict_result(ckcode_image_path)


class Crawler(object):
    page_restore_dir = './htmls/'
    def __init__(self, ck_cracker):
        self.ck_cracker = ck_cracker
        self.ckcode_image_path = './images/ckcode.jpg'
        m = re.search(r'Crawler(\w*)', str(self.__class__))
        if m:
            crawler_name = m.group(1)
            self.ckcode_image_path = './images/' +  crawler_name + '-ckcode.jpg'

        if not os.path.exists(self.ckcode_image_path):
            CrawlerUtils.make_dir(self.ckcode_image_path)

        print self.ckcode_image_path

    def crawl_work(self, ent_number = 0):
        self.ent_number = str(ent_number)
        self.page_restore_dir = self.__class__.page_restore_dir + self.ent_number + '/'
        if not os.path.exists(self.page_restore_dir):
            CrawlerUtils.make_dir(self.page_restore_dir)

        self.opener = CrawlerUtils.make_opener()
        self.crawl_check_page()
        self.crawl_ind_comm_pub_pages()
        self.crawl_ent_pub_pages()
        self.crawl_other_dept_pub_pages()

    def crack_checkcode(self):
        checkcode_url =  self.get_checkcode_url()
        page = self.opener.open(checkcode_url).read()
        with open(self.ckcode_image_path, 'w') as f:
            f.write(page)
        return self.ck_cracker.crack(self.ckcode_image_path)

    #破解验证码
    def crawl_check_page(self):
        pass

    #工商公示信息
    def crawl_ind_comm_pub_pages(self):
        pass

    #企业公示信息
    def crawl_ent_pub_pages(self):
        pass

    #其他部门公示信息
    def crawl_other_dept_pub_pages(self):
        pass

    #司法协助公示信息
    def crawl_judical_assist_pub_pages(self):
        pass
