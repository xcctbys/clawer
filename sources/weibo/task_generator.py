#encoding=utf-8
""" example is http://s.weibo.com/weibo/%25E5%25A5%25BD%25E7%259A%2584?topnav=1&wvr=6&b=1
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
import datetime


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR
    
logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")




class History(object):
    START_DATE = datetime.datetime(2015, 7, 1)
    KEYWORDS = [
        u"3D打印",
        u"三维打印",
        u"3D医疗打印",
        u"智能穿戴设备",
        u"可穿戴设备",
        u"穿戴式智能设备",
        u"智能手环",
        u"智能手表",
        u"苹果手机",
        u"苹果平板电脑",
        u"苹果电脑",
        u"苹果笔记本",
        u"苹果手表",
        u"iPhone",
        u"iPad", 
        u"MacBook",
        u"Mac", 
        u"iMac", 
        u"MacBook Air", 
        u"MacBook Pro",
        u"大数据", 
        u"hadoop",
        u"MapReduce",
        u"NoSQL 数据库",
        u"数据挖掘",
        u"机器学习",
        u"基因检测", 
        u"DNA检测",
        u"DNA测序",
        u"基因测序", 
        u"基因谱测序",
        u"血液DNA检测",
        u"体液DNA检测",
        u"机器人",
        u"智能机器人", 
        u"工业机器人",
        u"机器宠物",
        u"无人驾驶飞机",
        u"无人机", 
        u"无人直升机",
        u"无人固定翼机",
        u"无人多旋翼飞行器",
        u"无人飞艇",
        u"无人伞翼机",
        u"物联网",
        u"物联网产业", 
        u"RFID标签", 
        u"智能标签",
        u"新能源",
        u"再生能源",
        u"清洁能源",
        u"太阳能",
        u"光能",
        u"光伏",
        u"光伏电池",
        u"风能",
        u"生物质能",
        u"氢能",
        u"地热能",
        u"海洋能",
        u"化工能",
        u"核能",
        u"核电",
        u"移动支付",
        u"手机支付",
        u"二维码支付",
        u"指纹指付",
        u"支付宝",
        u"NFC",
        u"近场支付",
        u"云计算",
        u"云安全",
        u"云储存", 
        u"基础设施即服务",
        u"平台即服务",
        u"软件即服务",
        u"智慧城市",
        u"数字城市",
        u"无线城市",
        u"智能城市",
        u"智能医疗",
        u"智慧医疗",
        u"移动医疗",
        u"远程医疗",
        u"电子医疗",
        u"智慧医院系统",
        u"区域卫生系统",
        u"家庭健康系统",
        u"Wise Information Technology of 120",
        u"智能电视",
        u"智能机顶盒",
        u"智能电网",
        u"智电电力",
        u"电网2.0",
        u"电网智能化",
        u"现代电网",
        u"互动电网",
        u"智能家居",
        u"智慧楼宇",
        u"家庭自动化",
        u"电子家居",
        u"家庭网络",
        u"信息家电",
        u"智能汽车",
        u"智能驾驶系统",
        u"无人驾驶汽车",
        u"自动驾驶汽车",
        u"新能源汽车",
        u"智能手机",
        u"平板电脑", 
        u"平板计算机",
        u"移动电脑",
        u"4G 网络", 
        u"LTE网络",
        u"iPhone", 
        u"iPad",
        u"Galaxy",
        u"Surface平板电脑",
        u"工业4.0",
        u"智能工厂",
        u"智能生产",
        u"智能制造",
        u"工业自动化",
    ]
    
    
    def __init__(self):
        self.current_date = self.START_DATE
        self.path = "/tmp/weibo"
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
            self.current_date = old.current_date
    
    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)
        



class Generator(object):
    HOST = "http://s.weibo.com/"
    COOKIE = """SUB=_2A257IzEmDeTxGedI71sX9C_OyzuIHXVYWSXurDV8PUNbuNAPLXbQkW8a15WxqSXUU-MajF3cVrtZ0IQZjA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W575wlC1KuW1YMkoNNR1dnY5JpX5K2t
; UOR=os.51cto.com,widget.weibo.com,www.52ml.net; SINAGLOBAL=3410159700720.107.1445223309661; ULV=1445406910212
:2:2:2:8597766366396.563.1445406910172:1445223309665; NSC_wjq_txfjcp_mjotij=ffffffff094113d745525d5f4f58455e445a4a423660
; WBStore=4e40f953589b7b00|undefined; _s_tentry=-; Apache=8597766366396.563.1445406910172; WBtopGlobal_register_version
=23fff18db09017ad; SUS=SID-1649641207-1445413238-XD-47b6k-6a10ab4cff5097aa597c8895fa7388d4; SUE=es%3Ddbba2759e2fd677b8f0c530fda8d0861
%26ev%3Dv1%26es2%3D03588079ee33d6821b2bcc631c83ec50%26rs0%3DdlU5t1U57rNc5SmnOjVXC39RxH5CwM1nsnkQXSRFkLLme1
%252FiXtcx8NLGnVIZ%252F1rQzmslCc0pwNUH%252FcskYEkf0%252BBBLtynI6%252Bkq0R2aSKlxmGySPrS9iNvGMXnJPr%252FsGHBZxnFvC
%252BQLjGsNS53j7pPDkA5wWL8YAMkP%252FAY2EaSJNU%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1445413238%26et%3D1445499638
%26d%3Dc909%26i%3D88d4%26us%3D1%26vf%3D2%26vt%3D1%26ac%3D25%26st%3D0%26uid%3D1649641207%26name%3Dyyaadet2002
%2540gmail.com%26nick%3D%25E6%2599%2593%25E6%25B6%259B%26fmp%3D%26lcp%3D2012-02-03%252014%253A23%253A28
; SUHB=0D-EYZw22O0SgM; ALF=1446018038; SSOLoginState=1445413238; un=yyaadet2002@gmail.com
    """
    STEP = 10
    
    def __init__(self):
        self.uris = set()
        self.history = History()
        try:
            pwname = pwd.getpwnam("nginx")
            self.uid = pwname.pw_uid
            self.gid = pwname.pw_gid
        except:
            logging.error(traceback.format_exc(10))
            
        self.history.load()
            
    def obtain_urls(self):
        now = datetime.datetime.now()
        end = self.history.current_date + datetime.timedelta(10)
        if end > now:
            end = now
            
        while self.history.current_date.date() < end.date():
            for keyword in self.history.KEYWORDS:
                logging.debug("keyword is %s", keyword)
                for page in range(1, self.STEP+1):
                    self.uris.add(self.pack_url(keyword, page, self.history.current_date))
                    logging.debug(u"date %s, keyword %s", self.history.current_date, keyword)
            
            self.history.current_date += datetime.timedelta(1)
            self.history.save()
                
    def pack_url(self, keyword, page, dt):
        word = urllib.quote(keyword.encode("utf-8"))
        word = urllib.quote(word)
        start = dt.strftime("%Y-%m-%d-0")
        end = (dt + datetime.timedelta(1)).strftime("%Y-%m-%d-0")
        return urlparse.urljoin(self.HOST, "/weibo/%s&typeall=1&suball=1&timescope=custom:%s:%s&page=%d" % (word, start, end, page))
    

class GeneratorTest(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def test_obtain_urls(self):
        self.generator = Generator()
        self.generator.obtain_urls()
        
        logging.debug("urls count is %d", len(self.generator.uris))
        
        self.assertGreater(len(self.generator.uris), 0)
        
        

if __name__ == "__main__":
    if DEBUG:
        unittest.main()
        
    generator = Generator()
    generator.obtain_urls()
    for uri in generator.uris:
        print json.dumps({"uri":uri, "cookie":generator.COOKIE.strip()})