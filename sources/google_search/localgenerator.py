# encoding=utf-8
""" example is https://www.google.com.hk/webhp?hl=zh-CN&as_q=&as_epq=&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=&cr=&as_qdr=w&as_sitesearch=&as_occt=any&safe=active&as_filetype=&as_rights=#newwindow=1&safe=strict&hl=zh-CN&tbs=qdr:w&q=ipone

"""

import urllib
import logging
import unittest
import datetime

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
        u'工业自动化',
        u'additive manufacturing',
        u'rapid prototyping',
        u'3D printing',
        u'3D printer',
        u'filament',
        u'makerbot',
        u'Wearable device',
        u'Wearable smart device',
        u'Smart Bracelet',
        u'Smart Watch',
        u'big data',
        u'NoSQL database',
        u'in-memory analytics',
        u'Data Warehouse',
        u'data mining',
        u'machine learning',
        u'Genetic testing',
        u'DNA testing',
        u'DNA sequencing',
        u'Gene test',
        u'genetic diagnosis',
        u'Blood DNA test',
        u'Body fluid DNA test',
        u'Robot',
        u'Industrial Robot AI',
        u'Artificial Intelligence',
        u'factory automation',
        u'UAV',
        u'Unmanned aerial vehicle',
        u'remotely piloted aircraft',
        u'RPA',
        u'Drone revolution',
        u'Drone Delivery',
        u'Unmanned helicopter',
        u'Unmanned fixed wing aircraft',
        u'Unmanned airship',
        u'Unmanned wing aircraft',
        u'Internet of things',
        u'IoT',
        u'RFID',
        u'M2M',
        u'Internet of Everything',
        u'New Energy',
        u'alternative energy',
        u'renewable energy',
        u'clean energy',
        u'Renewable energy',
        u'Solar energy',
        u'Wind energy',
        u'Biomass energy',
        u'Hydrogenic energy',
        u'Geothermal energy',
        u'Ocean energy',
        u'Chemical energy',
        u'Nuclear energy',
        u'Mobile payment',
        u'mobile money',
        u'mobile money transfer',
        u'mobile wallet',
        u'NFC payment',
        u'QR code payments',
        u'cloud computing',
        u'cloud safety',
        u'cloud storage',
        u'IaaS',
        u'PaaS',
        u'SaaS',
        u'Smart city',
        u'smart community',
        u'Smart city',
        u'Digital city',
        u'Wireless city',
        u'Mhealth',
        u'Mobile health',
        u'Mobile Healthcare',
        u'Remote patient monitoring',
        u'RPM',
        u'telehealth',
        u'eHealth',
        u'Intelligent hospital system',
        u'Regional health system',
        u'Home health system',
        u'Smart TV',
        u'connected TV',
        u'hybrid TV',
        u'set-top box',
        u'internet TV',
        u'Online interactive media',
        u'On-demanding streaming media',
        u'Smart grid',
        u'Smart Power Grids',
        u'intelligent grid',
        u'intelligent power grids',
        u'Smart home',
        u'home automation',
        u'building automation',
        u'intelligent home',
        u'E-home',
        u'digital home',
        u'home networking',
        u'Intelligent Vehicles',
        u'Intelligent driving',
        u'driverless car',
        u'self-driving car',
        u'autonomous vehicle',
        u'electric vehicles',
        u'Smart Phone',
        u'smartphone',
        u'tablet',
        u'Tablet PC',
        u'iPhone',
        u'iPad',
        u'Galaxy',
        u'Surface Tablet',
        u'Industrie 4.0',
        u'smart factory',
        u'Smart Manufacturing'

]


class Generator(object):
    HOST = "https://www.google.com.hk/search?"

    def __init__(self):
        self.uris = set()

    def obtain_urls(self, star_time, end_time):
        for each in keywords:
            url = self.HOST + urllib.urlencode({"q": each.encode("utf8")}) + '&lr=&newwindow=1&safe=strict&hl=zh-CN&as_qdr=all&source=lnt&tbs=cdr%3A1%2Ccd_min%3A' + starTime + '%2Ccd_max%3A' + endTime + '&tbm='
            self.uris.add(url)


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls(starTime, endTime)

        logging.debug("urls count is %d", len(self.generator.uris))

        self.assertGreater(len(self.generator.uris), 0)


if __name__ == "__main__":
    # 实现任何日期运行都能锁定时间跨度为最近的周三到周二（当前周周一运行时生成时间跨度为上上周三到上周二,当前周周三运行时生成时间跨度为上周三到这周二...）
    weekday = datetime.datetime.today().weekday()
    if weekday < 2:
        starTime = (datetime.datetime.now() - datetime.timedelta(days=weekday + 12)).strftime("%Y-%m-%d")
        endTime = (datetime.datetime.now() - datetime.timedelta(days=weekday + 6)).strftime("%Y-%m-%d")
    else:
        starTime = (datetime.datetime.now() - datetime.timedelta(days=weekday + 5)).strftime("%Y-%m-%d")
        endTime = (datetime.datetime.now() - datetime.timedelta(days=weekday - 1)).strftime("%Y-%m-%d")

    if DEBUG:
        unittest.main()

    generator = Generator()
    generator.obtain_urls(starTime, endTime)
    sName = str(starTime) + "-" + str(endTime)
    f = open(sName + ".txt", "w+")  # 创建txt文本并写入url
    for uri in generator.uris:
        f.write(uri)
        f.write("\n")
    f.close()
