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
    masker = 255
    to_denoise = True
    pixel_index = 1

    def __init__(self, captcha_type="beijing"):
        '''

        :param captcha_type:
            captcha_type用于选择模型类型和验证码分割位置.

            beijing
            jiangsu
            zongju: for national gov and shanghai
            zhongwen: for Anhui, Guangxi, Heilongjiang, Henan
            guangdong: for Guangdong Province
        :return: None
        '''

        captcha_type = captcha_type.lower()
        if captcha_type not in ["jiangsu", "beijing", "zongju", "zhongwen", "guangdong"]:
            exit(1)
        elif captcha_type in ["jiangsu", "beijing", "zongju"]:
            self.label_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                               "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                               "a", "s", "d", "f", "g", "h", "j", "k", "l", "z",
                               "x", "c", "v", "b", "n", "m"]
            self.to_denoise = True
            self.masker = 255
        elif captcha_type in ["guangdong"]:
            self.to_denoise = True
            self.masker = 255
            self.label_list = [u"零", u"壹", u"贰", u"叁", u"肆", u"伍", u"陆", u"柒", u"捌", u"玖", u"拾", u"加", u"减", u"乘", u"除",
                               u"等", u"于"]
        elif captcha_type in ["zhongwen"]:
            self.to_denoise = False
            self.masker = 200
            self.pixel_index = 0
            self.label_list = [u"禁", u"退", u"茂", u"待", u"骇", u"怀", u"谈", u"舌", u"随", u"逐", u"沓", u"辕", u"渔", u"抗", u"外",
                               u"尘", u"悛", u"缚", u"宝", u"造", u"虚", u"瞥", u"两", u"儆", u"攮", u"岳", u"欲", u"合", u"方", u"尸",
                               u"强", u"线", u"放", u"见", u"血", u"铃", u"翅", u"幄", u"勇", u"呈", u"棋", u"反", u"经", u"金", u"恐",
                               u"矛", u"狗", u"庸", u"若", u"睚", u"话", u"此", u"喑", u"泣", u"止", u"知", u"鹤", u"周", u"士", u"罪",
                               u"语", u"马", u"浮", u"衰", u"念", u"年", u"其", u"摸", u"达", u"材", u"阔", u"吃", u"的", u"娇", u"针",
                               u"栋", u"羊", u"颐", u"缕", u"五", u"首", u"错", u"星", u"颠", u"会", u"弥", u"假", u"走", u"枪", u"犬",
                               u"是", u"脱", u"草", u"吁", u"割", u"朵", u"窟", u"户", u"图", u"改", u"耻", u"晋", u"阿", u"参", u"雄",
                               u"顺", u"聋", u"恶", u"鹏", u"跎", u"烹", u"插", u"何", u"黔", u"典", u"教", u"移", u"行", u"欢", u"黄",
                               u"来", u"令", u"秦", u"火", u"捭", u"差", u"声", u"围", u"穷", u"沫", u"鹿", u"巾", u"梁", u"态", u"弄",
                               u"沉", u"上", u"窍", u"后", u"底", u"算", u"默", u"蒙", u"攘", u"军", u"业", u"猜", u"盾", u"缤", u"倦",
                               u"用", u"添", u"河", u"枯", u"惜", u"惑", u"足", u"娲", u"纵", u"离", u"为", u"抽", u"鬼", u"壁", u"维",
                               u"雅", u"篇", u"蓉", u"效", u"秋", u"然", u"苍", u"歌", u"掌", u"郑", u"绕", u"永", u"祥", u"富", u"晚",
                               u"孜", u"迟", u"胡", u"逑", u"牢", u"以", u"坤", u"让", u"铩", u"兰", u"竭", u"柯", u"盲", u"饰", u"色",
                               u"请", u"偶", u"击", u"智", u"竽", u"荼", u"老", u"指", u"领", u"颖", u"舍", u"完", u"树", u"息", u"北",
                               u"袖", u"必", u"弟", u"怡", u"鹰", u"责", u"春", u"群", u"茧", u"梦", u"渝", u"冰", u"唳", u"阵", u"真",
                               u"涸", u"人", u"精", u"秀", u"久", u"衷", u"胆", u"词", u"克", u"囊", u"前", u"双", u"杏", u"桑", u"晕",
                               u"返", u"南", u"淘", u"妻", u"牝", u"鳞", u"觑", u"卧", u"门", u"八", u"雪", u"杯", u"冠", u"归", u"卷",
                               u"惶", u"汹", u"养", u"建", u"烟", u"使", u"泾", u"宁", u"刀", u"射", u"蜀", u"枉", u"渭", u"祖", u"再",
                               u"而", u"鼎", u"玑", u"成", u"儒", u"气", u"化", u"辙", u"丘", u"力", u"蔚", u"钟", u"弓", u"计", u"嚣",
                               u"尤", u"披", u"到", u"纲", u"水", u"挈", u"昔", u"王", u"所", u"奂", u"病", u"荆", u"陈", u"立", u"重",
                               u"彩", u"李", u"发", u"结", u"面", u"藕", u"膏", u"乘", u"明", u"贻", u"非", u"寡", u"骑", u"代", u"兢",
                               u"日", u"学", u"器", u"浪", u"偬", u"置", u"叱", u"机", u"怒", u"熙", u"延", u"迹", u"胫", u"技", u"如",
                               u"眉", u"班", u"程", u"世", u"复", u"小", u"美", u"笑", u"隙", u"栗", u"戛", u"次", u"己", u"鸣", u"咤",
                               u"骥", u"眩", u"别", u"薪", u"夭", u"微", u"母", u"阳", u"冲", u"电", u"家", u"弹", u"纸", u"炼", u"晴",
                               u"十", u"观", u"故", u"遇", u"鼠", u"蝉", u"手", u"背", u"城", u"孑", u"狐", u"角", u"取", u"余", u"绘",
                               u"牛", u"风", u"胜", u"江", u"连", u"荡", u"章", u"革", u"雨", u"扫", u"瘦", u"危", u"平", u"赵", u"瓴",
                               u"偷", u"叶", u"相", u"闺", u"好", u"柔", u"突", u"侃", u"堂", u"字", u"分", u"争", u"月", u"残", u"尊",
                               u"与", u"窑", u"府", u"酒", u"倒", u"斯", u"喘", u"优", u"肝", u"夜", u"作", u"辣", u"逢", u"锤", u"在",
                               u"莫", u"簪", u"涯", u"花", u"眸", u"去", u"尺", u"礼", u"举", u"心", u"遂", u"几", u"毋", u"藏", u"虎",
                               u"子", u"法", u"姗", u"诺", u"仙", u"毛", u"驴", u"狡", u"占", u"恢", u"歧", u"沐", u"黩", u"热", u"公",
                               u"路", u"英", u"石", u"赴", u"引", u"能", u"诣", u"应", u"威", u"薄", u"备", u"三", u"逍", u"倍", u"于",
                               u"我", u"缺", u"鼓", u"昙", u"情", u"逝", u"生", u"掠", u"营", u"大", u"称", u"温", u"缝", u"关", u"贯",
                               u"暮", u"爱", u"现", u"悲", u"鸟", u"状", u"丹", u"友", u"政", u"难", u"烂", u"居", u"奇", u"肠", u"义",
                               u"里", u"敏", u"从", u"扑", u"提", u"当", u"族", u"忘", u"乎", u"釜", u"回", u"珠", u"履", u"照", u"齐",
                               u"幽", u"卫", u"泪", u"恭", u"姬", u"目", u"巴", u"梨", u"虹", u"死", u"臼", u"长", u"蛾", u"羁", u"琴",
                               u"循", u"躇", u"言", u"醉", u"鲋", u"踌", u"愎", u"斑", u"吐", u"肓", u"暗", u"妙", u"枝", u"东", u"功",
                               u"境", u"接", u"座", u"锦", u"潜", u"怨", u"咫", u"鞭", u"犯", u"安", u"露", u"仓", u"贤", u"纷", u"禹",
                               u"治", u"欺", u"羽", u"帼", u"暴", u"旁", u"荣", u"蛇", u"凉", u"半", u"口", u"淑", u"青", u"盗", u"窠",
                               u"筚", u"总", u"苟", u"神", u"形", u"继", u"恨", u"泰", u"端", u"饮", u"深", u"壳", u"穴", u"价", u"赶",
                               u"快", u"炙", u"尔", u"逃", u"垂", u"骄", u"万", u"殊", u"服", u"龙", u"徒", u"茕", u"帘", u"肘", u"君",
                               u"厚", u"朝", u"障", u"舟", u"多", u"狱", u"瀣", u"甚", u"有", u"天", u"墨", u"措", u"躬", u"由", u"耳",
                               u"帷", u"悸", u"莺", u"流", u"桃", u"巷", u"陇", u"鸠", u"光", u"屋", u"及", u"钧", u"绌", u"燎", u"救",
                               u"道", u"财", u"单", u"潸", u"飘", u"诚", u"萤", u"衣", u"矢", u"步", u"璧", u"左", u"磨", u"眦", u"迫",
                               u"良", u"楼", u"玩", u"寒", u"陷", u"时", u"腹", u"郸", u"百", u"载", u"穿", u"岁", u"市", u"将", u"肉",
                               u"趋", u"貉", u"林", u"墙", u"涛", u"戚", u"蜜", u"原", u"善", u"没", u"交", u"换", u"报", u"横", u"亭",
                               u"本", u"田", u"防", u"猴", u"德", u"点", u"眼", u"吴", u"铁", u"过", u"名", u"淋", u"答", u"志", u"嚎",
                               u"绝", u"杜", u"秣", u"童", u"孤", u"忧", u"全", u"转", u"可", u"数", u"至", u"干", u"缨", u"迷", u"裹",
                               u"酸", u"闻", u"空", u"国", u"填", u"顾", u"谁", u"殄", u"沆", u"栉", u"锋", u"不", u"炎", u"向", u"众",
                               u"怙", u"问", u"丝", u"果", u"亢", u"室", u"徙", u"峰", u"思", u"紫", u"中", u"振", u"新", u"亲", u"鸿",
                               u"负", u"根", u"画", u"猿", u"直", u"渡", u"场", u"宠", u"懈", u"魏", u"郎", u"还", u"乾", u"比", u"罗",
                               u"恙", u"九", u"远", u"孟", u"飞", u"象", u"无", u"团", u"古", u"聩", u"约", u"韬", u"山", u"女", u"曲",
                               u"银", u"项", u"蠢", u"白", u"翼", u"极", u"一", u"玉", u"戈", u"事", u"同", u"渐", u"途", u"编", u"战",
                               u"愚", u"喝", u"蛛", u"映", u"索", u"沧", u"伦", u"掩", u"身", u"理", u"断", u"听", u"邯", u"惺", u"辱",
                               u"粉", u"锲", u"破", u"莹", u"杞", u"施", u"吼", u"迁", u"信", u"纶", u"华", u"乐", u"霸", u"联", u"工",
                               u"四", u"楚", u"川", u"食", u"濡", u"拣", u"觥", u"车", u"科", u"落", u"武", u"闭", u"惯", u"俱", u"买",
                               u"晨", u"对", u"井", u"任", u"得", u"簇", u"按", u"滥", u"下", u"休", u"沙", u"夕", u"悔", u"轮", u"益",
                               u"实", u"诱", u"刚", u"驰", u"动", u"仆", u"蹉", u"疲", u"谷", u"赤", u"阻", u"膺", u"卑", u"耿", u"宾",
                               u"雀", u"充", u"捉", u"拈", u"之", u"扬", u"网", u"叹", u"打", u"汗", u"高", u"瓜", u"今", u"靡", u"因",
                               u"巢", u"入", u"厉", u"韦", u"自", u"体", u"灯", u"影", u"已", u"兵", u"筹", u"登", u"出", u"柳", u"避",
                               u"开", u"处", u"文", u"帆", u"誉", u"庭", u"福", u"戎", u"云", u"斗", u"阖", u"芙", u"甜", u"舞", u"亡",
                               u"张", u"掣", u"谢", u"肥", u"愤", u"斧", u"带", u"助", u"株", u"地", u"讳", u"头", u"犹", u"瞻", u"沽",
                               u"阋", u"仁", u"杀", u"求", u"装", u"兄", u"聊", u"界", u"绑", u"坐", u"毓", u"兔", u"旗", u"湖", u"遥",
                               u"进", u"聚", u"蓝", u"镜", u"荐", u"满", u"挑", u"钓", u"伥", u"晦", u"择", u"矫", u"苦", u"哭", u"敬",
                               u"扮", u"彰", u"右", u"僵", u"旷", u"倾", u"泽", u"荫", u"凿", u"瘁", u"往", u"岂", u"者", u"源", u"了",
                               u"守", u"朋", u"萍", u"涌", u"意", u"洗", u"暖", u"望", u"悚", u"尝", u"喜", u"椟", u"鸡", u"鞠", u"欣",
                               u"倥", u"货", u"亦", u"末", u"邪", u"谭", u"男", u"先", u"鼻", u"尽", u"始", u"漓", u"间", u"千", u"鹊",
                               u"起", u"细", u"惊", u"绿", u"运", u"擒", u"期", u"盖", u"睛", u"襟", u"竞", u"忠", u"正", u"波", u"补",
                               u"凤", u"物", u"诨", u"睫", u"厦", u"狮", u"即", u"灵", u"致", u"海", u"骨", u"驹", u"司", u"轻", u"曾",
                               u"命", u"西", u"漫"]

        if captcha_type == "jiangsu":
            self.image_label_count = 6
            self.image_start = 0
            self.image_width = 20
            self.image_height = 47
            self.image_top = 3
            self.image_gap = 5
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
                else:
                    _pixel_data.append(1.0 if captcha_image.getpixel((i, j))[self.pixel_index] > self.masker else 0.0)
        return _pixel_data

    def __convertPoint__(self, image_path):
        _data = []
        try:
            im = Image.open(image_path)
            (width, height) = im.size
            if self.to_denoise:
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
            labels = image_label_pair.iloc[i]["value"]
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
        return predict_result