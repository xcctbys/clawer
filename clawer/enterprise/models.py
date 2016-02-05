#encoding=utf-8

from django.db import models


class Province(object):
    (ANHUI, 
     BEIJING) = range(1, 3)
      
    choices = (
        (ANHUI, u"安徽"),
        (BEIJING, u"北京"),
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
    
    