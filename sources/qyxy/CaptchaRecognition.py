# -*- coding:UTF-8 -*-
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
import pandas as pd
import os
import numpy as np
from sklearn.svm import SVC
from sklearn.externals import joblib


class CaptchaRecognition(object):
    image_start = 30  # start postion of first number
    image_width = 30  # width of each number
    image_height = 47  # end postion from top
    image_top = 3  # start postion of top
    image_gap = 0
    _value_label = {}
    image_label_count = 4
    pixel_zero = 255

    def __init__(self, captcha_type="beijing"):

        if captcha_type not in ["jiangsu", "beijing"]:
            exit(1)
        else:
            self.label_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                               "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                               "a", "s", "d", "f", "g", "h", "j", "k", "l", "z",
                               "x", "c", "v", "b", "n", "m"]

        if captcha_type == "jiangsu":
            self.image_label_count = 6
            self.image_start = 0
            self.image_width = 20
            self.image_height = 47
            self.image_top = 3
            self.image_gap = 5

        self.model_path = "model/" + captcha_type
        self.model_file = self.model_path + "/model.m"

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

    def __convertPoint__(self, image_path):
        _data = []
        try:
            im = Image.open(image_path)
            (width, height) = im.size
            im = im.filter(ImageFilter.MedianFilter())
            enhancer = ImageEnhance.Contrast(im)
            im = enhancer.enhance(10)
            im = im.convert('1')
            for k in range(self.image_label_count):
                left = max(0, self.image_start + self.image_width * k + self.image_gap * k)
                right = min(self.image_start + self.image_width * (k + 1) + self.image_gap * k, width)
                sub_image = im.crop((left, self.image_top, right, self.image_height))
                pixel_list = self.__get_pixel_list__(sub_image)
                if k == 0:
                    _data = np.array([pixel_list])
                else:
                    _data = np.append(_data, [pixel_list], axis=0)
            return _data
        except IOError:
            pass

    # def __get_images__(self, image_path):
    #     images = []
    #     for image in os.listdir(image_path):
    #         if image != ".DS_Store":
    #             images.append(image_path + "/" + image)
    #     return images

    def update_model(self, image_path, label_file):
        if not os.path.isdir(self.model_path):
            os.mkdir(self.model_path)
        if not os.path.isdir(image_path):
            exit(1)

        image_label_pair = pd.read_csv(label_file)
        index = 0
        X = []
        y = []
        y_count = 0
        for i in range(len(image_label_pair)):
            image = image_path + "/" + str(image_label_pair.iloc[i]["name"])
            labels = image_label_pair.iloc[i]["value"]
            for i in range(self.image_label_count):
                y.append(labels[i])
                y_count += 1
            if index == 0:
                X = self.__convertPoint__(image)
            else:
                X = np.append(X, self.__convertPoint__(image), axis=0)
            index += 1
        model = SVC().fit(X, y)
        joblib.dump(model, self.model_file)
        return True

    def predict_result(self, image_path):
        if os.path.isfile(self.model_file):
            self.clf = joblib.load(self.model_file)
        else:
            raise IOError
        pixel_matrix = self.__convertPoint__(image_path)
        predict_result = ""
        for feature in pixel_matrix:
            _f = np.array([feature], dtype=np.float)
            predict_result += str(self.label_list[self.clf.predict(_f)[0]])
        return predict_result
