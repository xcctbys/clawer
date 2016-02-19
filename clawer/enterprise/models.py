#encoding=utf-8

from django.db import models


class Province(object):
    (ANHUI,
     BEIJING,
     CHONGQING,
     FUJIAN,
     GANSU,
     GUANGDONG,
     GUANGXI,
     GUIZHOU,
     HAINAN,
     HEBEI,
     HEILONGJIANG,
     HENAN,
     HUBEI,
     HUNAN,
     JIANGSU,
     JIANGXI,
     JILIN,
     LIAONING,
     NEIMENGGU,
     NINGXIA,
     QINGHAI,
     SHAANXI,
     SHANDONG,
     SHANGHAI,
     SHANXI,
     SICHUAN,
     TIANJIN,
     XINJIANG,
     YUNNAN,
     ZHEJIANG,
     ZONGJU,
     XIZANG) = range(1, 33)

    choices = (
        (ANHUI, u"安徽"),
        (BEIJING, u"北京"),
        (CHONGQING, u"重庆"),
        (FUJIAN, u"福建"),
        (GANSU, u"甘肃"),
        (GUANGDONG, u"广东"),
        (GUANGXI, u"广西"),
        (GUIZHOU, u"贵州"),
        (HAINAN, u"海南"),
        (HEBEI, u"河北"),
        (HEILONGJIANG, u"黑龙江"),
        (HENAN, u"河南"),
        (HUBEI, u"湖北"),
        (HUNAN, u"湖南"),
        (JIANGSU, u"江苏"),
        (JIANGXI, u"江西"),
        (JILIN, u"吉林"),
        (LIAONING, u"辽宁"),
        (NEIMENGGU, u"内蒙古"),
        (NINGXIA, u"宁夏"),
        (QINGHAI, u"青海"),
        (SHAANXI, u"陕西"),
        (SHANDONG, u"山东"),
        (SHANGHAI, u"上海"),
        (SHANXI, u"山西"),
        (SICHUAN, u"四川"),
        (TIANJIN, u"天津"),
        (XINJIANG, u"新疆"),
        (YUNNAN, u"云南"),
        (ZHEJIANG, u'浙江'),
        (ZONGJU, u"总局"),
        (ZONGJU, u"西藏"),
    )

    @classmethod
    def to_name(cls, province):
        for item in cls.choices:
            if item[0] == province:
                return item[1]

        return None

    @classmethod
    def to_id(cls, name):
        for item in cls.choices:
            if item[1] == name:
                return item[0]

        return None



class Enterprise(models.Model):
    name = models.CharField(max_length=256)
    province = models.IntegerField(max_length=128, choices=Province.choices)
    register_no = models.CharField(max_length=128)
    add_datetime = models.DateTimeField(auto_now_add=True)

    def as_json(self):
        result = {"id": self.id,
            "name": self.name,
            "province": self.province,
            "province_name": Province.to_name(self.province),
            "register_no": self.register_no,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result


