#encoding=utf-8

from django.db import models
from django.conf import settings
import urlparse

# Create your models here.

class Category(object):
    (NORMAL, YUNSUAN, ZHIHU, JIANGSHU,
     TIANJIN,
     JIANGXI,
     CHONGQING,
     SICHUAN,
     GUIZHOU,
     XIZHUANG,
     QINHAI,
     NINGXIA,
     XINJIANG,
     QUANGUO,
     GUANGDONG,
     SHANGHAI,
     HEBEI,
     ALL,
     #天津、江西、重庆、四川、贵州、西藏、山西、青海、宁夏、新疆
     ) = range(1, 19)
    
    choices = (
        (NORMAL, u"普通字母"),
        (YUNSUAN, u"运算类型"),
        (ZHIHU, u"知乎字母"),
        (JIANGSHU, u"江苏"),
        (TIANJIN, u"天津"),
        (JIANGXI, u"江西"),
        (CHONGQING, u"重庆"),
        (SICHUAN, u"四川"),
        (GUIZHOU, u"贵州"),
        (XIZHUANG, u"西藏"),
        (QINHAI, u"青海"),
        (NINGXIA, u"宁夏"),
        (XINJIANG, u"新疆"),
        (QUANGUO, u"全国"),
        (GUANGDONG, u"广东"),
        (SHANGHAI, u"上海"),
        (ALL, u"全国工商总局"),
        (HEBEI, u"河北"),
    )
    
    @classmethod
    def name(cls, category):
        for item in cls.choices:
            if item[0] == category:
                return item[1]
        
        return ""


class Captcha(models.Model):
    url = models.URLField()
    category = models.IntegerField(choices=Category.choices)
    image_hash = models.CharField(max_length=32)
    label_count = models.IntegerField(default=0)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "captcha"
    
    def image_url(self):
        return urlparse.urljoin(settings.MEDIA_URL, "captcha/%d/%s" % (self.category, self.image_hash))
    
    def label_logs(self):
        return LabelLog.objects.filter(captcha=self)
    
    def as_json(self):
        result = {"id": self.id,
            "category": self.category,
            "image_hash": self.image_hash,
            "labels": [x.label for x in self.label_logs()],
            "image_url": self.image_url(),
        }
        return result
        
        
class LabelLog(models.Model):
    captcha = models.ForeignKey(Captcha)
    label = models.CharField(max_length=32)
    ip = models.IPAddressField()
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "captcha"
        

