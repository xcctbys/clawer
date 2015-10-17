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
import cv2
import numpy as np
from matplotlib import pyplot as plt



DEBUG = True
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


class TrainCaptcha(object):
    def __init__(self, d):
        self.save_dir = "train"
        self.image_url = d["image_url"]
        self.image_hash = d["image_hash"]
        if os.path.exists(self.save_dir) is False:
            os.makedirs(self.save_dir, 0775)
            
    def raw_path(self):
        return os.path.join(self.save_dir, self.image_hash)
    
    def gray_path(self):
        return os.path.join(self.save_dir, self.image_hash, "_gray")
        
    def filter(self):
        raw_im = cv2.imread(self.raw_path())
        gray_im = cv2.cvtColor(raw_im, cv2.COLOR_BGR2GRAY)
        mean_thresholding_im = cv2.adaptiveThreshold(gray_im, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
        blur_im = cv2.medianBlur(mean_thresholding_im, 5)
        
        ims = [
            [raw_im, "raw"],
            [gray_im, "gray"],
            [mean_thresholding_im, "mean thresholding"],
            [blur_im, "blur"],
        ]
        
        for i in range(len(ims)):
            [im, title] = ims[i]
            plt.subplot(4, 2, i+1)
            plt.imshow(im, "gray")
            plt.xticks([])
            plt.yticks([])
            plt.title("%s" % (title))
            
            
        
        plt.show()
        plt.close()        


class OpencvTrain(object):
    def __init__(self):
        self.api_url = "http://clawer.princetechs.com/captcha/all/labeled/?category=1"
        self.captchas = []
    
    def load_data(self):
        r = requests.get(self.api_url)
        if r.status_code != 200:
            logging.warn("failed to load api url, status code %d", r.status_code)
            return
        
        for item in r.json()["captchas"]:
            captcha = TrainCaptcha(item)
            self.captchas.append(captcha)
            save_path = captcha.raw_path()
            if os.path.exists(save_path):
                continue
            image_r = requests.get(captcha.image_url)
            with open(save_path, "w") as f:
                f.write(image_r.content)
                
    

class OcrTrainTest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    """
    def test_ocr(self):
        ocr = Ocr("http://qyxy.baic.gov.cn/CheckCodeCaptcha?currentTimeMillis=1444875766745&num=87786")
        ocr.to_text()
    """
     
        
class TestTrainCaptcha(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.opencv_train = OpencvTrain()
        self.opencv_train.load_data()
        
    def test_filter(self):
        train_captcha = self.opencv_train.captchas[0]
        train_captcha.filter()
        
    

if __name__ == "__main__":
    if DEBUG:
        unittest.main()
        
    opencv_train = OpencvTrain()
    opencv_train.load_data()
        