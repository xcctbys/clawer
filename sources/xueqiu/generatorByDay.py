# coding=utf-8
""" example is http://xueqiu.com/k?q=iphone
"""

import logging
import json
import urllib
import unittest
import requests
import traceback
import os
import datetime
import cPickle as pickle
try:
    import pwd
except:
    pass


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


keywords = [
        u'3D打印',
        u'三维打印',
        u'3D医疗打印',
        u'智能穿戴设备',
        u'可穿戴设备',
        u'穿戴式智能设备',
        u'智能手环',
        u'智能手表',
        u'苹果手机',
        u'苹果平板电脑',
        u'苹果电脑',
        u'苹果笔记本',
        u'苹果手表',
        u'iPhone',
        u'iPad',
        u'MacBook',
        u'Mac',
        u'iMac',
        u'MacBook Air',
        u'MacBook Pro',
        u'大数据',
        u'hadoop',
        u'MapReduce',
        u'NoSQL 数据库',
        u'数据挖掘',
        u'机器学习',
        u'基因检测',
        u'DNA检测',
        u'DNA测序',
        u'基因测序',
        u'基因谱测序',
        u'血液DNA检测',
        u'体液DNA检测',
        u'机器人',
        u'智能机器人',
        u'工业机器人',
        u'机器宠物',
        u'无人驾驶飞机',
        u'无人机',
        u'无人直升机',
        u'无人固定翼机',
        u'无人多旋翼飞行器',
        u'无人飞艇',
        u'无人伞翼机',
        u'物联网',
        u'物联网产业',
        u'RFID标签',
        u'智能标签',
        u'新能源',
        u'再生能源',
        u'清洁能源',
        u'太阳能',
        u'光能',
        u'光伏',
        u'光伏电池',
        u'风能',
        u'生物质能',
        u'氢能',
        u'地热能',
        u'海洋能',
        u'化工能',
        u'核能',
        u'核电',
        u'移动支付',
        u'手机支付',
        u'二维码支付',
        u'指纹指付',
        u'支付宝',
        u'NFC',
        u'近场支付',
        u'云计算',
        u'云安全',
        u'云储存',
        u'基础设施即服务',
        u'平台即服务',
        u'软件即服务',
        u'智慧城市',
        u'数字城市',
        u'无线城市',
        u'智能城市',
        u'智能医疗',
        u'智慧医疗',
        u'移动医疗',
        u'远程医疗',
        u'电子医疗',
        u'智慧医院系统',
        u'区域卫生系统',
        u'家庭健康系统',
        u'智能电视',
        u'智能机顶盒',
        u'智能电网',
        u'智电电力',
        u'电网2.0',
        u'电网智能化',
        u'现代电网',
        u'互动电网',
        u'智能家居',
        u'智慧楼宇',
        u'家庭自动化',
        u'电子家居',
        u'家庭网络',
        u'信息家电智能汽车',
        u'智能驾驶系统',
        u'无人驾驶汽车',
        u'自动驾驶汽车',
        u'新能源汽车智能手机',
        u'平板电脑',
        u'平板计算机',
        u'移动电脑',
        u'4G 网络',
        u'LTE网络',
        u'iPhone',
        u'iPad',
        u'Galaxy',
        u'Surface平板电脑',
        u'工业4.0',
        u'智能工厂',
        u'智能生产',
        u'智能制造',
        u'工业自动化'

]



class History(object):

    def __init__(self):
        self.date_now = datetime.datetime.now()
        self.current_page_num = 1
        self.current_keyword_num = 0
        self.path = "/tmp/xueqiuByDay"
        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))

    def load(self):
        if os.path.exists(self.path) is False:
            return

        with open(self.path, "r") as f:
            old = pickle.load(f)
            if old.date_now.strftime("%Y-%m-%d") == self.date_now.strftime("%Y-%m-%d"):
                self.current_page_num = old.current_page_num
                self.current_keyword_num = old.current_keyword_num
            else:
                self.date_now = datetime.datetime.now()
                self.current_page_num = 1
                self.current_keyword_num = 0

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)



class Generator(object):
    HOST = "http://xueqiu.com/statuses/search.json?"
    MAXPAGE = 6

    def __init__(self):
        self.uris = ''
        self.cookie = ''
        self.history = History()
        self.history.load()

    def search_url(self):
        if self.history.current_page_num > self.MAXPAGE:
            self.history.current_page_num = 1
            self.history.current_keyword_num += 1
            self.history.save()
        self.page_url(keywords[self.history.current_keyword_num])

    def page_url(self, keyword):
        r = requests.get("http://xueqiu.com/", headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"})
        xq_a_token = r.cookies["xq_a_token"]
        current_cookie = "xq_a_token=" + xq_a_token + "; path=/; domain=.xueqiu.com; HttpOnly"
        url = self.HOST + urllib.urlencode({"page": str(self.history.current_page_num)}) + "&" + urllib.urlencode({"q": keyword.encode("utf8")})
        jscontent = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36", "cookie": current_cookie}).text
        js_dict = json.loads(jscontent)
        js_count = js_dict.get("count")
        if js_count == None:
            self.history.current_page_num = 1
            self.history.current_keyword_num += 1
            self.history.save()
            return
        self.obtain_urls(url, current_cookie)

    def obtain_urls(self , url, cookie):
        self.uris = url
        self.cookie = cookie
        self.history.current_page_num += 1
        self.history.save()




class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.search_url()


        logging.debug("urls is %s", self.generator.uris)
        logging.debug("cookie is %s", self.generator.cookie)



if __name__ == "__main__":

    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.search_url()

    print json.dumps({"uri":generator.uris, "cookie":generator.cookie})