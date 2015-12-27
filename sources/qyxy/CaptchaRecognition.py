# -*- coding:UTF-8 -*-
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
import pandas as pd
import os
import re
import numpy as np
from AntiNoise import AntiNoise
from sklearn.svm import SVC
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib

class CaptchaRecognition(object):
    image_start = 30  # start postion of first number
    image_width = 30  # width of each number
    image_height = 47  # end postion from top
    image_top = 3  # start postion of top
    image_gap = 0
    image_label_count = 4
    masker = 255
    to_denoise = True
    pixel_index = 1
    to_calculate = False
    customized_postisions = False
    double_denoise = False
    customized_width = None
    position_left = None
    position_right = None
    to_binarized = False
    to_summarized = False

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
        if captcha_type not in ["jiangsu", "beijing", "zongju", "liaoning", "guangdong", "hubei", "tianjin",
                                "qinghai", "shanxi", "henan", "guangxi", "xizang", "heilongjiang", "anhui", "shaanxi",
                                "ningxia", "chongqing", "sichuan", "hunan", "gansu", "xinjiang", "guizhou", "shandong",
                                "neimenggu", "zhejiang","jilin","yunnan"]:
            exit(1)
        elif captcha_type in ["jiangsu", "beijing", "zongju", "liaoning"]:
            self.label_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                               "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                               "a", "s", "d", "f", "g", "h", "j", "k", "l", "z",
                               "x", "c", "v", "b", "n", "m"]
            self.to_denoise = True
            self.masker = 255
        elif captcha_type in ["guangdong", "hubei", "tianjin", "qinghai", "shanxi", "henan", "guangxi", "xizang",
                              "heilongjiang", "anhui", "shaanxi", "ningxia", "chongqing", "sichuan", "hunan", "gansu",
                              "xinjiang", "guizhou", "shandong", "neimenggu", "zhejiang","jilin","yunnan"]:
            self.to_denoise = True
            self.masker = 255
            self.to_calculate = True
            self.label_list = [u"零", u"壹", u"贰", u"叁", u"肆", u"伍", u"陆", u"柒", u"捌", u"玖", u"拾", u"加", u"减", u"乘", u"除",
                               u"等", u"于", u"以", u"上", u"去", u"?", u"0", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8",
                               u"9", u"的", u"一", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九", u"十", u"〇", u"是"]
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
            self.to_binarized = True
            self.masker = 150
        elif captcha_type in ["yunnan", "fujian"]:
            self.image_label_count = 3
            self.margin = 8
            self.customized_postisions = True
            self.position_left = [0, 40, 74]
            self.position_right = [40, 80, 110]
            self.image_top = 5
            self.image_height = 38
            self.image_width = 160
            self.to_denoise = False
            self.customized_width = 25
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 540
            self.to_summarized = True
            self.anti_noise = True
            captcha_type = "yunnan"
        elif captcha_type == "chongqing":
            self.image_label_count = 6
            self.masker = 40
            self.customized_postisions = True
            self.position_left = [0, 23, 40, 65, 85, 105]
            self.position_right = [15, 45, 60, 90, 110, 120]
            self.image_top = 8
            self.image_height = 40
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = True
            self.customized_width = 25
            self.double_denoise = False
        elif captcha_type in ["sichuan","xinjiang]:
            self.image_label_count = 5
            self.masker = 110
            self.customized_postisions = True
            self.position_left = [3, 18, 35, 49, 65]
            self.position_right = [14, 35, 45, 65, 80]
            self.image_top = 0
            self.image_height = 30
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = True
            self.customized_width = 20
            self.double_denoise = False
        elif captcha_type == "hunan":
            self.margin = 8
            self.image_label_count = 3
            self.masker = 450
            self.customized_postisions = True
            self.position_left = [0, 28, 68, 96, 128]
            self.position_right = [30, 68, 108, 131, 160]
            self.image_top = 5
            self.image_height = 35
            self.image_width = 160
            self.to_denoise = False
            self.to_calculate = False
            self.to_binarized = True
            self.customized_width = 25
            self.anti_noise = True
        elif captcha_type == "gansu":
            self.image_label_count = 3
            self.customized_postisions = True
            self.position_left = [5, 19, 37]
            self.position_right = [19, 37, 55]
            self.image_top = 25
            self.image_height = 45
            self.to_denoise = False
            self.customized_width = 20
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 580
            self.to_summarized = True
        elif captcha_type == "hubei":
            self.image_label_count = 5
            # self.masker = 110
            self.customized_postisions = True
            self.position_left = [3, 27, 56, 79, 95]
            self.position_right = [28, 57, 82, 97, 124]
            self.image_top = 0
            self.image_height = 40
            self.to_denoise = False
            self.customized_width = 32
            self.double_denoise = False
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 445
            self.to_summarized = True
        elif captcha_type == "shandong":
            self.image_label_count = 4
            self.customized_postisions = True
            self.position_left = [10, 29, 54, 74]
            self.position_right = [29, 54, 74, 93]
            self.image_top = 12
            self.image_height = 32
            self.to_denoise = False
            self.customized_width = 30
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 370
            self.to_summarized = True
        elif captcha_type == "jilin":
            self.image_label_count = 4
            self.customized_postisions = True
            self.position_left = [13, 34, 53, 73]
            self.position_right = [34, 53, 73, 94]
            self.image_top = 12
            self.image_height = 32
            self.to_denoise = False
            self.customized_width = 30
            self.to_calculate = False
            self.to_binarized = False
            self.masker = 410
            self.to_summarized = True
        elif captcha_type == "ningxia":
            self.image_label_count = 6
            self.masker = 100
            self.customized_postisions = True
            self.position_left = [15, 40, 70, 89, 126, 144]
            self.position_right = [40, 72, 89, 126, 144, 160]
            self.image_top = 0
            self.image_height = 40
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = True
            self.customized_width = 40
            self.double_denoise = False
        elif captcha_type == "shaanxi":
            self.image_label_count = 5
            self.masker = 110
            self.customized_postisions = True
            self.position_left = [0, 16, 35, 49, 65]
            self.position_right = [15, 35, 44, 65, 80]
            self.image_top = 0
            self.image_height = 30
            self.to_denoise = False
            self.to_binarized = True
            self.customized_width = 30
            self.double_denoise = False
            self.to_calculate = True
        elif captcha_type in ["qinghai", "shanxi", "henan", "guangxi", "xizang", "heilongjiang", "anhui"]:
            self.image_label_count = 5
            self.masker = 420
            self.customized_postisions = True
            self.position_left = [6, 30, 59, 82, 95, 125, 150]
            self.position_right = [28, 57, 81, 100, 135, 155, 175]
            self.image_top = 15
            self.image_height = 50
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = False
            self.customized_width = 40
            self.double_denoise = False
            self.to_summarized = True
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
                elif self.to_summarized:
                    _pixel_data.append(0.0 if sum(captcha_image.getpixel((i, j))) > self.masker else 1.0)
                else:
                    _pixel_data.append(1.0 if captcha_image.getpixel((i, j))[self.pixel_index] > self.masker else 0.0)
        if self.customized_width is not None:
            difference = self.customized_width - width
            half = difference / 2
            _pixel_data = [0.0] * half * height + _pixel_data + [0.0] * height * (difference - half)
        return _pixel_data

    def __convertPoint__(self, image_path):
        _data = []
        if not self.anti_noise:
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
        else:
            an = AntiNoise(image_path, self.masker)
            pixels = an.pixels
            self.__update_positions__(pixels)
            for i in range(self.image_label_count):
                left = self.position_left[i]
                right = self.position_right[i]
                pixel_list = []
                height = self.image_height - self.image_top
                for x in range(left, right):
                    for y in range(self.image_top, self.image_height):
                        pixel_list.append(pixels[y][x])
                if self.customized_width is not None:
                    difference = self.customized_width - (right - left)
                    half = difference / 2
                    pixel_list = [0.0] * half * height + pixel_list + [0.0] * height * (difference - half)
                if i == 0:
                    _data = np.array([pixel_list])
                else:
                    _data = np.append(_data, [pixel_list], axis=0)

            return _data

    def update_model(self, image_path, label_file, train_size):
        if not os.path.isdir(self.model_path):
            os.mkdir(self.model_path)
        if not os.path.isdir(image_path):
            exit(1)

        image_label_pair = pd.read_csv(label_file, encoding="utf-8")
        image_label_pair = image_label_pair[:train_size]
        index = 0
        x = []
        y = []
        y_count = 0
        start = datetime.datetime.now()
        start_time = datetime.datetime.now()
        for i in range(len(image_label_pair)):
            image = image_path + "/" + str(image_label_pair.iloc[i]["name"])
            labels = image_label_pair.iloc[i]["value"]
            if type(labels) == int:
                labels = str(labels)
            for l in range(self.image_label_count):
                y.append(self.label_list.index(labels[l]))
                y_count += 1
            if index == 0:
                x = self.__convertPoint__(image)
            else:
                x = np.append(x, self.__convertPoint__(image), axis=0)
            # print len(y), len(x)
            index += 1
            end_time = datetime.datetime.now()
            if i in range(0, len(image_label_pair), len(image_label_pair) / 20):
                print u"数据集已完成:", round(float(i) / len(image_label_pair), 4) * 100, "%", u"所用时间:", end_time - start_time
                start_time = datetime.datetime.now()
        print u"数据集已生成 共用时", datetime.datetime.now() - start, u"开始建模"
        rbm = BernoulliRBM(random_state=0, verbose=True, learning_rate=0.02, n_iter=400, n_components=650,
                           batch_size=12)
        svm = SVC(kernel="linear", tol=5e-14, class_weight="balanced")
        classifier = Pipeline(steps=[("rbm", rbm), ("svm", svm)])
        model = classifier.fit(x, y)
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
        if len(numbers) < 1:
            return 2
        elif len(numbers) == 1:
            first_num = self.__convert_to_number__(numbers[0])
            if results.__contains__(u"乘"):
                if first_num == 0:
                    return 0
                else:
                    return first_num * 2
            else:
                return first_num

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
        elif first_num == 0 or second_num == 0:
            return 0
        else:
            return first_num + second_num


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