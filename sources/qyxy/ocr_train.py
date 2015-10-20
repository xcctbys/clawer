#encoding=utf-8
""" required: opencv and tesseract
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
import cv2
import numpy as np
from matplotlib import pyplot as plt



DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.WARNING
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")




class Ocr(object):
    def __init__(self, image_path, image_hash):
        self.tesseract = "/usr/local/bin/tesseract"
        self.chinese = None
        self.english = None
        self.image_path = image_path
        self.image_hash = image_hash
        
    def to_text(self):
        parent = os.path.dirname(__file__)
        out_chi = os.path.join(parent, "%s_chi" % (self.image_hash))
        subprocess.call([self.tesseract, self.image_path, out_chi, "-l", "chi_sim", "-psm", "7"])
        out_chi += ".txt"
        with open(out_chi, "r") as f:
            self.chinese = unicode(f.read().strip(), "utf-8")
        os.remove(out_chi)
            
        out_eng = os.path.join(parent, "%s_eng" % (self.image_hash))
        subprocess.call([self.tesseract, self.image_path, out_eng, "-l", "eng", "-psm", "8"])
        out_eng += ".txt"
        with open(out_eng, "r") as f:
            self.english = f.read()
        os.remove(out_eng)
        
        new_english = ""
        for c in self.english.strip():
            if c.isdigit() or c.isalpha():
                new_english += c
        self.english = unicode(new_english, "utf-8")


class TrainCaptcha(object):
    def __init__(self, d):
        self.save_dir = "train"
        self.image_url = d["image_url"]
        self.image_hash = d["image_hash"]
        self.labels = d["labels"]
        if os.path.exists(self.save_dir) is False:
            os.makedirs(self.save_dir, 0775)
            
    def raw_path(self):
        return os.path.join(self.save_dir, self.image_hash)
    
    def gray_path(self):
        return os.path.join(self.save_dir, self.image_hash+"_gray.jpeg")
        
    def filter(self):
        raw_im = cv2.imread(self.raw_path())
        gray_im = cv2.cvtColor(raw_im, cv2.COLOR_BGR2GRAY)
        ret, thresholding_im = cv2.threshold(gray_im, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        
        blur_im = cv2.medianBlur(thresholding_im, 1)
        
        contours, hierarchy = cv2.findContours(blur_im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        img = cv2.drawContours(blur_im, contours, -1, (0, 255, 0), 1)
        
        cv2.imwrite(self.gray_path(), blur_im)
        
        if DEBUG:
            print "contours count is %d " % len(contours), hierarchy
            ims = [
                [raw_im, "raw"],
                [gray_im, "gray"],
                
                [thresholding_im, "thresholding"],
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
             
    def human_label(self):
        result = None
        for i in range(len(self.labels)):
            guess = self.labels[i]
            for j in range(len(self.labels)):
                if i == j:
                    continue
                if self.labels[j] == guess:
                    result = guess
                    break
        
        if result:
            result = result.upper()
        
        return result
    
    def machine_label(self):
        self.filter()
        ocr = Ocr(self.gray_path(), self.image_hash)
        ocr.to_text()
        return ocr.english.strip().upper(), ocr.chinese.strip().upper()
                

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
                
    def train(self):
        success = 0
        total = len(self.captchas)
        for captcha in self.captchas:
            human_label = captcha.human_label()
            eng, chi = captcha.machine_label()
            if eng == human_label:
                success += 1
                print u"[sucess %d %.2f%%]: human %s, machine %s" % (success, float(success*100)/total, human_label, eng)
            else:
                print u"failed: human %s, machine %s" % (human_label, eng)
        
        print "total %d, success %d, %.2f%%" % (total, success, float(success*100)/total)
                
    

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
    opencv_train.train()
        