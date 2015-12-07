#-*- coding:UTF-8 -*-
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
import pandas as pd
import os
import numpy as np
from sklearn.svm import SVC
from sklearn.externals import joblib


class CaptchaRecognition(object):
    _s = 30  # start postion of first number
    _w = 30  # width of each number
    _h = 47  # end postion from top
    _t = 3  # start postion of top
    _value_label = {}

    def __init__(self):
        _list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                 "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                 "a", "s", "d", "f", "g", "h", "j", "k", "l", "z",
                 "x", "c", "v", "b", "n", "m"]

        for i in range(len(_list)):
            self._value_label[i] = _list[i]

        model_file = "model/svm_20151116.m"
        if os.path.isfile(model_file):
            self.clf = joblib.load(model_file)
        else:
            raise IOError

    def __get_pixel_list__(self, captcha_image):

        (width, height) = captcha_image.size
        _pixel_data = []
        for i in range(width):
            for j in range(height):
                if (captcha_image.getpixel((i, j)) == 255):
                    _pixel_data.append(0.0)
                else:
                    _pixel_data.append(1.0)
        return _pixel_data

    def __convertPoint__(self, image_dir):
        _data = []
        image_name = image_dir
        try:
            im = Image.open(image_name)
            (width, height) = im.size
            im = im.filter(ImageFilter.MedianFilter())
            enhancer = ImageEnhance.Contrast(im)
            im = enhancer.enhance(2)
            im = im.convert('1')
            for k in range(4):
                left = max(0, self._s + self._w * k)
                right = min(self._s + self._w * (k + 1), width)
                sub_image = im.crop((left, self._t, right, self._h))
                pixel_list = self.__get_pixel_list__(sub_image)
                if k == 0:
                    _data = np.array([pixel_list])
                else:
                    _data = np.append(_data, [pixel_list], axis=0)
            return _data
        except IOError:
            pass

    def predict_result(self, image_dir):
        pixel_matrix = self.__convertPoint__(image_dir)
        predict_result = ""
        for feature in pixel_matrix:
            _f = np.array([feature], dtype=np.float)
            predict_result += str(self._value_label[self.clf.predict(_f)[0]])
        return predict_result
