#encoding=utf-8
""" example is http://blog.sina.com.cn/s/articlelist_1300871220_0_1.html
"""


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


DEBUG = True
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")



SEARCH_ENTRY = [
    "http://qyxy.baic.gov.cn/beijing"
]


Enterprises = [
    {"name": u"安信证券股份有限公司北京分公司"}
] 


class Generator(object):
    STEP = 100
    
    def __init__(self):
        self.uris = set()
        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))

    

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
            
        out_chi = os.path.join(parent, "%s_chi" % image_id)
        subprocess.call([self.tesseract, path, out_chi, "-l", "chi_sim", "-psm", "7"])
        
        out_eng = os.path.join(parent, "%s_eng" % image_id)
        subprocess.call([self.tesseract, path, out_eng, "-l", "eng", "-psm", "7"])
        
        chi = ""
        with open(out_chi+".txt", "r") as f:
            chi = f.read()
            
        eng = ""
        with open(out_eng+".txt", "r") as f:
            eng = f.read()
        
        return (chi, eng)
        

class GeneratorTest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def test_ocr(self):
        ocr = Ocr("http://qyxy.baic.gov.cn/CheckCodeCaptcha?currentTimeMillis=1444875766745&num=87786")
        (chi, eng) = ocr.to_text()
        self.assertIsNotNone(chi)
        self.assertIsNotNone(eng)
        

if __name__ == "__main__":
    if DEBUG:
        unittest.main()
        
    generator = Generator()
    #generator.obtain_urls()
    for uri in generator.uris:
        print json.dumps({"uri":uri})
