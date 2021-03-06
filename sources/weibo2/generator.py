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
    KEYWORDS = [u"农业", u"林业", u"牧渔业", u"畜牧业", u"屠宰", u"肉类", u"农副产品", u"木材", u"家具", u"粮食", u"豆类", u"蔬菜", u"水果", u"谷类", u"棉花",
                u"农作物", u"灌溉", u"海水养殖", u"水产品", u"农业 ", u"肥料", u"绿化", u"园林", u"苗木", u"花卉", u"鲜花", u"苗圃", u"园林工程", u"园林绿化",
                u"园林设计", u"景观", u"景观设计", u"种子", u"边坡绿化", u"彩棉", u"草坪", u"插花", u"樱桃", u"防腐木材", u"花店", u"花艺", u"兰花", u"荔枝",
                u"芦荟", u"胚胎移植", u"人造草坪", u"生态园", u"食用菌", u"水产", u"渔网", u"渔具", u"渔业", u"牧业", u"奶牛", u"兽药", u"饲料", u"养殖",
                u"奶牛场", u"山羊", u"乳制品", u"农场", u"梯田", u"水稻", u"小麦", u"果林", u"鱼塘", u"采矿", u"煤炭", u"石油", u"盐业", u"煤制品", u"烟煤",
                u"无烟煤", u"褐煤", u"石煤", u"泥炭", u"风化煤", u"天然气", u"黑色金属", u"有色金属", u"土砂石", u"贵金属矿采", u"稀土金属", u"碳素", u"碳素制品",
                u"煤矿", u"石墨", u"原油", u"破磨", u"石灰石", u"铜矿", u"铁矿", u"金矿", u"银矿", u"石油化工", u"农业化工", u"化学医药", u"高分子材料", u"涂料",
                u"油脂", u"化工产品", u"有机化工", u"无机化工", u"合成染料", u"催化剂", u"水泥", u"化工", u"化妆品", u"橡胶", u"塑料", u"玻璃", u"润滑油",
                u"塑料制品", u"油漆", u"塑胶", u"陶瓷", u"橡胶制品", u"工业气体", u"聚丙烯纤维", u"建筑玻璃", u"铬酸酐", u"石油焦", u"防火玻璃", u"氟碳漆", u"真空贱镀",
                u"建筑涂料", u"三偏磷酸钠", u"涂料助剂", u"有机玻璃", u"磷酸", u"医药", u"聚氨酯", u"干燥剂", u"耐火材料", u"颜料", u"电镀", u"吸塑", u"化学试剂",
                u"染料", u"保护膜", u"胶粘剂", u"化工原料", u"乳胶漆", u"二氧化氯", u"乳化剂", u"护肤品", u"PVC", u"夜光粉", u"玻璃制品", u"精油", u"香薰",
                u"树脂", u"尼龙", u"绝缘漆", u"抗裂纤维", u"收缩膜", u"微粉", u"清洁剂", u"贵金属", u"沥青乳化剂", u"五氧化二磷", u"氧化锌", u"油酸酯", u"防腐",
                u"冶金", u"甘油", u"农药", u"硅胶", u"消毒剂", u"沥青", u"香料", u"杀虫剂", u"浆料", u"阻燃剂", u"絮凝剂", u"食用色素", u"饲料", u"磷化工",
                u"碳酸钙", u"活性炭", u"食品添加剂", u"清洁用品", u"密封胶", u"化工设备", u"空气污染", u"水污染", u"土壤污染", u"臭氧层破坏", u"炼铁", u"炼钢",
                u"钢加工", u"铁合金冶炼", u"钢丝", u"钢材", u"钢铁", u"钢筋", u"钢板", u"钢管", u"钢企", u"钢协", u"不锈钢", u"无缝钢管", u"铝型材", u"不锈钢管",
                u"带钢", u"型钢", u"优钢", u"钢锭", u"钢绞线", u"钢绳", u"锻造", u"铸钢", u"铸铁", u"焊管", u"东三省", u"提炼", u"冶金", u"高温", u"熔断",
                u"合金", u"餐饮", u"饭店", u"食品", u"正餐", u"中餐", u"晚餐", u"炒菜", u"主食", u"快餐", u"饮料", u"冷饮", u"茶馆", u"咖啡", u"酒吧",
                u"小吃", u"火锅", u"加盟连锁", u"披萨", u"奶茶", u"西点", u"川菜", u"团购", u"外卖", u"点菜系统", u"无线点菜", u"必胜客", u"肯德基", u"麦当劳",
                u"湘菜", u"粤菜", u"烤肉", u"料理", u"西餐", u"潮州菜", u"海鲜", u"淮扬菜", u"鲁菜", u"东北菜", u"本帮菜", u"清真", u"制造业", u"农副食品加工",
                u"饲料加工", u"植物油加工", u"制糖", u"肉类加工", u"水产品加工", u"谷物磨制", u"食品制造", u"酒制造", u"盐加工", u"饮料制造", u"烟草制品", u"纺织",
                u"服装制造", u"服饰制造", u"制鞋业", u"木材加工", u"家具制造", u"造纸", u"印刷", u"工艺品", u"皮具", u"纸业", u"箱包", u"礼品", u"皮革",
                u"人造毛皮", u"家具", u"五金", u"模具", u"自动化", u"机械加工", u"烟草制造", u"纺织业", u"造纸业", u"金属制品", u"塑料制品", u"电力", u"供水",
                u"废物处理", u"污水处理", u"燃气供应", u"交通", u"通讯", u"供气", u"供热", u"垃圾处理", u"公共交通事业", u"慈善", u"志愿行动", u"公共物品", u"公共服务",
                u"军事", u"外交", u"司法", u"教育", u"法律", u"治安管理", u"社会保障", u"社会福利", u"民政服务", u"劳教管理", u"司法部门", u"机关", u"社区",
                u"事业单位", u"社会团体", u"国家机构", u"铁路", u"公路", u"水运", u"航空", u"交通运输", u"旅客运输", u"货物运输", u"道路运输", u"管道运输", u"物流",
                u"货运", u"运输", u"汽车", u"轿车", u"吉普车", u"卡车", u"公交车", u"电动车", u"汽车租赁", u"自行车", u"托盘", u"仓储货架", u"周转箱", u"叉车",
                u"公路货运", u"航空货运", u"物流配送", u"物流网", u"集装箱", u"海运", u"配货", u"出租车", u"货运网", u"中铁", u"运输信息", u"运输业", u"飞机",
                u"轮船", u"电瓶车", u"摩托车", u"直升机", u"邮轮", u"私人快艇", u"房地产", u"物业管理", u"房屋租赁", u"房价", u"二手房", u"别墅", u"写字楼",
                u"租房", u"物业", u"房地产评估", u"楼盘", u"商品房", u"置业", u"CBD", u"厂房租赁", u"二手房买卖", u"房产测绘", u"房屋买卖", u"购物中心", u"土地开发",
                u"房地产泡沫", u"房地产贬值", u"房地产增值", u"万科", u"恒大", u"万达", u"绿城", u"批发", u"零售", u"服装", u"服饰", u"女装", u"童装", u"职业装",
                u"超市", u"商品流通", u"商品交易市场", u"货源", u"化妆品", u"膨化食品", u"饮料", u"饰品", u"烟草", u"建筑业", u"土木工程", u"工程建筑", u"建筑安装",
                u"电气安装", u"设备安装", u"建筑装饰", u"装修", u"装潢", u"建材", u"地板", u"保温材料", u"自动门", u"防水材料", u"装饰材料", u"彩钢", u"石材",
                u"卫浴", u"楼梯", u"塑胶跑道", u"防火门", u"采光板", u"防盗门", u"护栏", u"耐火材料", u"隔热材料", u"水泥", u"石灰", u"石膏", u"木质材料", u"隔音",
                u"吸声材料", u"防潮材料", u"绝缘材料", u"混凝土", u"砂浆", u"建筑设计", u"排水", u"结构", u"暖通", u"人防工程", u"工程管理", u"工程造价", u"新闻业",
                u"出版业", u"广播", u"电视", u"电影", u"文化艺术", u"娱乐业", u"电子游艺厅", u"歌舞厅", u"网吧", u"游乐园", u"歌厅", u"舞厅", u"游艺厅", u"台球厅",
                u"玩具", u"游乐设备", u"游戏机", u"电玩", u"话剧", u"酒吧", u"俱乐部", u"音乐", u"戏曲", u"戏剧", u"京剧", u"曲艺", u"杂技", u"评书",
                u"中国好声音", u"中国新歌声", u"我是歌手", u"欢乐喜剧人", u"极限挑战", u"奔跑吧兄弟", u"通信：苹果", u"三星", u"华为", u"小米", u"魅族", u"黑莓",
                u"通信", u"电信", u"无线电", u"电报", u"电话", u"通讯", u"邮政", u"视频会议", u"集团电话", u"对讲机", u"电话会议", u"IP电话", u"喇叭", u"雷达",
                u"耳机", u"网络电话", u"扬声器", u"远程教育", u"视频会议设备", u"视频会议系统", u"手机数据线", u"自助寄存柜", u"电话交换机", u"二极管", u"广播系统",
                u"呼叫中心", u"收音机", u"卫星电话", u"电脑", u"电缆", u"读卡器", u"发光二极管", u"光缆", u"摄像机", u"电信设备", u"电子白板", u"发光管", u"射频",
                u"全球卫星定位", u"电路板", u"射频设备", u"集成电路", u"光纤", u"晶体", u"无线网卡", u"无线局域网", u"卫星通讯", u"铁塔", u"蓝牙耳机", u"导航",
                u"导航监控", u"网桥", u"微波", u"半导体", u"磁卡"]


    def __init__(self):
        self.date_now = datetime.datetime.now()
        self.position = 0
        self.path = "/tmp/sina_weiboByDay2"
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
                self.position = old.position
            else:
                self.position = 0
                self.save()

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)
            if hasattr(self, "uid"):
                os.chown(self.path, self.uid, self.gid)




class Generator(object):
    HOST = "http://m.weibo.cn/page/pageJson"
    STEP = 2
    PAGE = 6

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
        end = self.history.position + self.STEP
        if end >= len(self.history.KEYWORDS):
            end = len(self.history.KEYWORDS)

        while self.history.position < end:
            keyword = self.history.KEYWORDS[self.history.position]

            for i in range(1, self.PAGE):
                self.uris.add(self.pack_url(keyword, i))

            self.history.position += 1
            self.history.save()

    def pack_url(self, keyword, page):
        qs = {
            "containerid":"",
            "containerid": (u"100103type=1&q=%s" % keyword).encode("utf-8"),
            "ext":"",
            "fid": (u"100103type=1&q=%s" % keyword).encode("utf-8"),
            "uicode": "10000011",
            "v_p":"11",
            "type":"all",
            "queryVal": keyword.encode("utf-8"),
            "page": page
        }
        return urlparse.urljoin(self.HOST, "?%s" % urllib.urlencode(qs))



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
        print json.dumps({"uri":uri})