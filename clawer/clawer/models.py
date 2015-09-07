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
            {"id":101, "text":u"失败任务", "url":"clawer.views.home.clawer_task_failed", "groups":GROUPS},
        ]},
        {"id":2, "text": u"系统管理", "url":"", "children": [
            {"id":201, "text":u"参数设置", "url":"", "groups":[GROUP_MANAGER]},
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
        runing =  self.runing_task_generator()
        if runing:
            result["runing_task_generator"] = runing.as_json()
        else:
            result["runing_task_generator"] = None
        return result
    
    def runing_task_generator(self):
        try:
            result = ClawerTaskGenerator.objects.filter(clawer=self, status=ClawerTaskGenerator.STATUS_ON)[0]
        except:
            result = None
        
        return result
        
        

class ClawerTaskGenerator(models.Model):
    (STATUS_ALPHA, STATUS_BETA, STATUS_PRODUCT, STATUS_ON, STATUS_OFF, STATUS_TEST_FAIL) = range(1, 7)
    STATUS_CHOICES = (
        (STATUS_ALPHA, u"alpha"),
        (STATUS_BETA, u"beta"),
        (STATUS_PRODUCT, u"production"),
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线"),
        (STATUS_TEST_FAIL, u"测试失败"),
    )
    clawer = models.ForeignKey(Clawer)
    code = models.TextField()  #python code
    cron = models.CharField(max_length=128)
    status = models.IntegerField(default=STATUS_ALPHA, choices=STATUS_CHOICES)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        ordering = ["-id"]
        
    def as_json(self):
        result = {"id": self.id,
            "clawer_id": self.clawer_id,
            "code": self.code,
            "cron": self.cron,
            "status": self.status,
            "status_name": self.status_name(),
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result
    
    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
        return ""
        

class ClawerTask(models.Model):
    (STATUS_LIVE, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS) = range(1, 5)
    STATUS_CHOICES = (
        (STATUS_LIVE, u"新增"),
        (STATUS_PROCESS, u"进行中"),
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    clawer = models.ForeignKey(Clawer)
    task_generator = models.ForeignKey(ClawerTaskGenerator)
    uri = models.CharField(max_length=4096)
    status = models.IntegerField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    add_datetime = models.DateTimeField(auto_now_add=True)
    done_datetime = models.DateTimeField(null=True, blank=True) #when fail or success
    
    class Meta:
        app_label = "clawer"
        ordering = ["-id"]
        
    def as_json(self):
        result = {"id":self.id,
            "clawer": self.clawer.as_json(),
            "task_generator": self.task_generator.as_json(),
            "uri": self.uri,
            "status": self.status,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "done_datetime": self.done_datetime.strftime("%Y-%m-%d %H:%M:%S") if self.done_datetime else None,
        }
        return result
