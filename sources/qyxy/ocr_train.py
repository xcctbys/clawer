#encoding=utf-8

import urllib
import json
import sys
import logging
import unittest
import requests
import os
import cPickle as pickle

from bs4 import BeautifulSoup
import urlparse
import pwd
import traceback
import hashlib
import subprocess



DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.WARNING
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")




class Ocr(object):
    def __init__(self, url):
        self.url = url
        self.tesseract = "/usr/local/bin/tesseract"
        
    def to_text(self):
        r = requests.get(self.url)
        if r.status_code != 200:
            logging.warn("request %s failed, status code %d", self.url, r.status_code)
            return None
        image_id = hashlib.md5(self.url).hexdigest()[-6:]
        parent = "/Users/pengxt/Documents/ocr"
        if os.path.exists(parent) is False:
            os.makedirs(parent, 0775)
        
        path = os.path.join(parent, image_id)
        with open(path, "w") as f:
            f.write(r.content)
        
        for page in range(0, 11): 
            out_chi = os.path.join(parent, "%s_chi_%d" % (image_id, page))
            subprocess.call([self.tesseract, path, out_chi, "-l", "chi_sim", "-psm", str(page)])
            
            out_eng = os.path.join(parent, "%s_eng_%d" % (image_id, page))
            subprocess.call([self.tesseract, path, out_eng, "-l", "eng", "-psm", str(page)])
            

class ImageLib(object):
    def __init__(self):
        self.url = "http://qyxy.baic.gov.cn/CheckCodeCaptcha?currentTimeMillis=1444875766745&num=87786"
        self.count = 10000
        self.save_dir = "/Users/pengxt/Documents/ocr/train_data"
        if os.path.exists(self.save_dir) is False:
            os.makedirs(self.save_dir, 0775)
        
    def download(self):
        for i in range(0, self.count):
            r = requests.get(self.url)
            if r.status_code != 200:
                logging.warn("request %s failed, status code %d", self.url, r.status_code)
                continue
            
            image_id = hashlib.md5(r.content).hexdigest()[-6:]
            path = os.path.join(self.save_dir, image_id)
            if os.path.exists(path):
                logging.warn("%d: %s exists", i, image_id)
                continue
            
            with open(path, "w") as f:
                f.write(r.content)
            
            logging.error("Download %d, image id %s", i, image_id)
        
                
    

class OcrTrainTest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def test_ocr(self):
        ocr = Ocr("http://qyxy.baic.gov.cn/CheckCodeCaptcha?currentTimeMillis=1444875766745&num=87786")
        ocr.to_text()
        
    

if __name__ == "__main__":
    if DEBUG:
        unittest.main()
        
    image_lib = ImageLib()
    image_lib.download()
        