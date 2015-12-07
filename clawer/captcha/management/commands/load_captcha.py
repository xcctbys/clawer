# coding=utf-8

import os
from optparse import make_option
import requests
import logging
import hashlib

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from captcha.models import Captcha, Category





class DownloadCaptcha(object):
    def __init__(self, url, category):
        self.url = url
        self.count = 300
        self.category = category
        self.save_dir = os.path.join(settings.CAPTCHA_STORE, "%d" % self.category)
        if os.path.exists(self.save_dir) is False:
            os.makedirs(self.save_dir, 0775)
        
    def download(self):
        finished = Captcha.objects.filter(category=self.category).count()
        if finished > self.count:
            return 
        
        for i in range(0, self.count - finished):
            r = requests.get(self.url)
            if r.status_code != 200:
                logging.warn("request %s failed, status code %d", self.url, r.status_code)
                continue
            
            image_hash = hashlib.md5(r.content).hexdigest()
            path = os.path.join(self.save_dir, image_hash)
            if os.path.exists(path):
                logging.warn("%d: %s exists", i, image_hash)
                continue
            
            with open(path, "w") as f:
                f.write(r.content)
                
            captcha = Captcha.objects.create(url=self.url, category=self.category, image_hash=image_hash)
            logging.debug("Download %d, image id %s, captcha id %d", i, image_hash, captcha.id)
        
        
    

class Command(BaseCommand):
    args = ""
    help = "Obtain all captcha."
    
    def __init__(self):
        self.urls = [
            [Category.NORMAL, "http://qyxy.baic.gov.cn/CheckCodeCaptcha?currentTimeMillis=1444875766745&num=87786"],
            [Category.YUNSUAN, "http://qyxy.baic.gov.cn/CheckCodeYunSuan?currentTimeMillis=1447655192940&num=48429"],
            [Category.ZHIHU, "http://www.zhihu.com/captcha.gif?r=1448087287415"],
            [Category.JIANGSHU, "http://www.jsgsj.gov.cn:58888/province/rand_img.jsp?type=7"],
            [Category.TIANJIN, "http://tjcredit.gov.cn/verifycode"],
            [Category.JIANGXI, "http://gsxt.jxaic.gov.cn/ECPS/verificationCode.jsp"],
            [Category.CHONGQING, "http://gsxt.cqgs.gov.cn/sc.action?width=130&height=40&fs=23&t=1449473139130"],
            [Category.SICHUAN, 'http://gsxt.scaic.gov.cn/ztxy.do?method=createYzm&dt=1449473634428&random=1449473634428'],
            [Category.GUIZHOU, 'http://gsxt.gzgs.gov.cn/search!generateCode.shtml?validTag=searchImageCode&1449473693892'],
            [Category.XIZHUANG, 'http://gsxt.xzaic.gov.cn/validateCode.jspx?type=0&id=0.6980565481876813'],
            [Category.QINHAI, 'http://218.95.241.36/validateCode.jspx?type=0&id=0.9130336582967944'],
            [Category.NINGXIA, 'http://gsxt.ngsh.gov.cn/ECPS/verificationCode.jsp?_=1449473855952'],
            [Category.XINJIANG, 'http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=createYzm&dt=1449473880582&random=1449473880582'],
        ]
    
    @wrapper_raven
    def handle(self, *args, **options):
        
        for item in self.urls:
            downloader = DownloadCaptcha(item[1], item[0])
            downloader.download()
        