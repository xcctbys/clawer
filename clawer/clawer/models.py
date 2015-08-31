#encoding=utf-8
import copy

from django.contrib.auth.models import User as DjangoUser
from django.db import models


class UserProfile(models.Model):
    (GROUP_MANAGER, GROUP_DEVELOPER) = (u"管理员", u"开发者")
    user = models.OneToOneField(DjangoUser)
    nickname = models.CharField(max_length=64)
    
    class Meta:
        app_label = "clawer"
        
    def as_json(self):
        return {"id": self.user.id,
            "nickname": self.nickname,
            "username": self.user.username,
        }


class MenuPermission:
    GROUP_MANAGER = UserProfile.GROUP_MANAGER
    GROUP_DEVELOPER = UserProfile.GROUP_DEVELOPER
    
    GROUPS = [
        GROUP_MANAGER,
        GROUP_DEVELOPER,
    ]
    
    MENUS = [
        {"id":1, "text": u"爬虫管理", "url":"", "children": [
            {"id":101, "text":u"查询爬虫", "url":"clawer.views.home.clawer_all", "groups":GROUPS},
        ]},
    ]
    
    @classmethod
    def has_perm_to_enter(cls, user):
        ret = False
        for group in user.groups.all():
            if group.name in cls.GROUPS:
                ret = True
                break
        
        return ret
    
    @classmethod
    def user_menus(cls, user):
        """ Return list of menus, format is:
        [
            {}
        ]
        """
        from django.core.urlresolvers import reverse
        
        menus = []
        user_group_names = set([x.name for x in user.groups.all()])
        
        def has_group(menu_groups):
            for name in user_group_names:
                if name in menu_groups:
                    return True
            return False
        
        for item in cls.MENUS: 
            new_item = copy.deepcopy(item)
            new_item["children"] = []
            
            for menu in item["children"]:
                if has_group(menu["groups"]):
                    new_menu = copy.deepcopy(menu)
                    if menu["url"]:
                        new_menu["url"] = reverse(menu["url"])
                    del new_menu["groups"]
                    new_item["children"].append(new_menu)
            menus.append(new_item)
        
        return menus

        

class Clawer(models.Model):
    name = models.CharField(max_length=128)
    info = models.CharField(max_length=1024)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        
    def as_json(self):
        result = {"id": self.id,
            "name": self.name,
            "info": self.info,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S")
        }
        return result
        

class ClawerTaskGenerator(models.Model):
    (STATUS_ALPHA, STATUS_BETA, STATUS_PRODUCT, STATUS_ON, STATUS_OFF) = range(1, 6)
    STATUS_CHOICES = (
        (STATUS_ALPHA, u"alpha"),
        (STATUS_BETA, u"beta"),
        (STATUS_PRODUCT, u"production"),
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线"),
    )
    clawer = models.ForeignKey(Clawer)
    code = models.TextField()  #python code
    cron = models.CharField(max_length=128)
    status = models.IntegerField(default=STATUS_ON, choices=STATUS_CHOICES)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        

class ClawerTask(models.Model):
    (STATUS_LIVE, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS) = range(1, 5)
    STATUS_CHOICES = (
        (STATUS_LIVE, u"新增"),
        (STATUS_PROCESS, u"进行中"),
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    clawer = models.ForeignKey(Clawer)
    clawer_generator = models.ForeignKey(ClawerTaskGenerator)
    uri = models.CharField(max_length=4096)
    status = models.IntegerField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    add_datetime = models.DateTimeField(auto_now_add=True)
    done_datetime = models.DateTimeField(null=True, blank=True) #when fail or success
    
    class Meta:
        app_label = "clawer"
        
