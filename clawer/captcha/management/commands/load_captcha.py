# coding=utf-8

import os
from optparse import make_option
import requests
import logging
import hashlib

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from captcha.models import Captcha


class Category(object):
    qyxy = 1
    



class QyxyCaptcha(object):
    def __init__(self):
        self.url = "http://qyxy.baic.gov.cn/CheckCodeCaptcha?currentTimeMillis=1444875766745&num=87786"
        self.count = 10000
        self.category = Category.qyxy
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
    option_list = BaseCommand.option_list + (
        make_option('--category',
            dest='category',
            default="qyxy",
            help='Captcha category. Default is qyxy. Values is [qyxy]'
        ),
    )
    
    @wrapper_raven
    def handle(self, *args, **options):
        if options["category"] == "qyxy":
            qyxy = QyxyCaptcha()
            qyxy.download()