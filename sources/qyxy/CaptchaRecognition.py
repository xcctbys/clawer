# -*- coding:UTF-8 -*-
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
import pandas as pd
import os
import re
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
    masker = 255
    to_denoise = True
    to_calculate = False
    pixel_index = 1

    def __init__(self, captcha_type="beijing"):
        '''

        :param captcha_type:
            captcha_type用于选择模型类型和验证码分割位置.

            beijing: for Beijing
            jiangsu: for Jiangsu Province
            zongju: for national gov and shanghai
            liaoning: for Liaoning Province
            guangdong: for Guangdong Province
            tianjin: for Tianjin Province
            hubei: for Hubei Province
        :return: None
        '''

        captcha_type = captcha_type.lower()
        if captcha_type not in ["jiangsu", "beijing", "zongju", "liaoning", "guangdong" ,"tianjin","hubei"]:
            exit(1)
        elif captcha_type in ["jiangsu", "beijing", "zongju", "liaoning"]:
            self.label_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                               "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                               "a", "s", "d", "f", "g", "h", "j", "k", "l", "z",
                               "x", "c", "v", "b", "n", "m"]
            self.to_denoise = True
            self.masker = 255
        elif captcha_type in ["guangdong", "hubei", "tianjin"]:
            self.to_denoise = True
            self.to_calculate = True
            self.masker = 255
            self.label_list = [u"零", u"壹", u"贰", u"叁", u"肆", u"伍", u"陆", u"柒", u"捌", u"玖", u"拾", u"加", u"减", u"乘", u"除",
                               u"等", u"于", u"以", u"上", u"去", u"?", u"0", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8",
                               u"9"]


        if captcha_type == "jiangsu":
            self.image_label_count = 6
            self.image_start = 0
            self.image_width = 20
            self.image_height = 47
            self.image_top = 3
            self.image_gap = 5
        elif captcha_type == "tianjin":
            self.image_label_count = 6
            self.customized_postisions = True
            self.position_left = [13, 40, 73, 104, 136, 162]
            self.position_right = [23, 60, 83, 119, 151, 172]
            self.image_top = 0
            self.image_height = 30
            self.to_denoise = False
            self.customized_width = 20
            self.to_calculate = True
            self.to_binarized = True
            self.masker = 150
        elif captcha_type == "hubei":
            self.image_label_count = 6
            self.masker = 110
            self.customized_postisions = True
            self.position_left = [0, 20, 50, 80, 100, 130]
            self.position_right = [30, 60, 80, 100, 130, 150]
            self.image_top = 0
            self.image_height = 40
            self.to_denoise = True
            self.to_calculate = False
            self.to_binarized = True
            self.customized_width = 40
            self.double_denoise = False
        elif captcha_type == "liaoning":
            self.image_label_count = 4
            self.image_start = 11
            self.image_width = 9
            self.image_height = 31
            self.image_top = 0
            self.image_gap = 11
            self.to_denoise = False
            self.masker = 254
        elif captcha_type == "zongju":
            self.image_label_count = 4
            self.image_start = 0
            self.image_width = 35
            self.image_height = 43
            self.image_top = 7
            self.image_gap = 5
        elif captcha_type in ["zhongwen"]:
            self.image_label_count = 4
            self.image_start = 27
            self.image_width = 25
            self.image_height = 50
            self.image_top = 0
            self.image_gap = 12
        elif captcha_type in ["guangdong"]:
            self.image_label_count = 5
            self.image_start = 26
            self.image_width = 25
            self.image_height = 40
            self.image_top = 0
            self.image_gap = 0


        self.model_path = "model/" + captcha_type
        self.model_file = self.model_path + "/model.m"

    def __get_pixel_list__(self, captcha_image):

        (width, height) = captcha_image.size
        _pixel_data = []
        for i in range(width):
            for j in range(height):
                if self.to_denoise:
                    pixel = captcha_image.getpixel((i, j))
                    if pixel == self.masker:
                        _pixel_data.append(0.0)
                    else:
                        _pixel_data.append(1.0)
                elif self.to_binarized:
                    _pixel_data.append(1.0 if captcha_image.getpixel((i, j)) < self.masker else 0.0)
                else:
                    _pixel_data.append(1.0 if captcha_image.getpixel((i, j))[self.pixel_index] > self.masker else 0.0)
        if self.customized_width is not None:
            difference = self.customized_width - width
            half = difference / 2
            _pixel_data = [0.0] * half * height + _pixel_data + [0.0] * height * (difference - half)
        return _pixel_data

    def __convertPoint__(self, image_path):
        _data = []
        try:
            im = Image.open(image_path)
            (width, height) = im.size
            if self.to_denoise:
                if self.double_denoise:
                    im = im.convert('L')
                im = im.filter(ImageFilter.MedianFilter())
                enhancer = ImageEnhance.Contrast(im)
                im = enhancer.enhance(10)
                im = im.convert('L')
            elif self.to_binarized:
                im = im.convert("L")
            for k in range(self.image_label_count):
                if not self.customized_postisions:
                    left = max(0, self.image_start + self.image_width * k + self.image_gap * k)
                    right = min(self.image_start + self.image_width * (k + 1) + self.image_gap * k, width)
                else:
                    left = self.position_left[k]
                    right = self.position_right[k]
                sub_image = im.crop((left, self.image_top, right, self.image_height))
                pixel_list = self.__get_pixel_list__(sub_image)
                if k == 0:
                    _data = np.array([pixel_list])
                else:
                    try:
                        _data = np.append(_data, [pixel_list], axis=0)
                    except:
                        print image_path, len(pixel_list), len(_data[0])
                        exit(1)
            return _data
        except IOError:
            pass

    def update_model(self, image_path, label_file):
        if not os.path.isdir(self.model_path):
            os.mkdir(self.model_path)
        if not os.path.isdir(image_path):
            exit(1)

        image_label_pair = pd.read_csv(label_file, encoding="utf-8")
        index = 0
        x = []
        y = []
        y_count = 0
        for i in range(len(image_label_pair)):
            image = image_path + "/" + str(image_label_pair.iloc[i]["name"])
            labels = str(image_label_pair.iloc[i]["value"])
            for l in range(self.image_label_count):
                try:
                    y.append(self.label_list.index(labels[l]))
                except:
                    print labels[l]
                y_count += 1
            if index == 0:
                x = self.__convertPoint__(image)
            else:
                x = np.append(x, self.__convertPoint__(image), axis=0)
            index += 1
        model = SVC(kernel="linear", class_weight="auto", tol=1e-15).fit(x, y)
        joblib.dump(model, self.model_file)
        return True

    def __convert_to_number__(self, number):
        digits = {u"零": 0, u"〇": 0, u"壹": 1, u"贰": 2, u"叁": 3, u"肆": 4, u"伍": 5, u"陆": 6, u"柒": 7, u"捌": 8, u"玖": 9,
                  u"拾": 10}
        number_in_digit = ""
        for n in number:
            number_in_digit += n if n not in digits else str(digits[n])
        return int(number_in_digit)

    def __calculate__(self, results):

        number_pattern = u"[0-9壹贰叁肆伍陆柒捌玖拾零]+"
        numbers = re.findall(number_pattern, results)
        if len(numbers) < 2:
            return 2

        first_num = self.__convert_to_number__(numbers[0])
        second_num = self.__convert_to_number__(numbers[1])

        if results.__contains__(u"加"):
            return first_num + second_num
        elif results.__contains__(u"减"):
            return first_num - second_num
        elif results.__contains__(u"乘"):
            return first_num * second_num
        elif results.__contains__(u"除"):
            return first_num / second_num
        else:
            return 0


    def predict_result(self, image_path):
        if os.path.isfile(self.model_file):
            self.clf = joblib.load(self.model_file)
        else:
            raise IOError
        pixel_matrix = self.__convertPoint__(image_path)
        predict_result = u""
        for feature in pixel_matrix:
            _f = np.array([feature], dtype=np.float)
            predict = self.clf.predict(_f)[0]
            predict_result += unicode(self.label_list[int(predict)])

        if self.to_calculate:
            return self.__calculate__((predict_result))
        else:
            return predict_result