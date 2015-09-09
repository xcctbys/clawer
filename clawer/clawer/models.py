#encoding=utf-8
import copy
import os
import logging
import datetime
import codecs

from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.conf import settings
from django.utils.encoding import smart_str


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
            {"id":101, "text":u"爬虫配置", "url":"clawer.views.home.clawer_all", "groups":GROUPS},
            {"id":102, "text":u"爬虫失败任务", "url":"clawer.views.home.clawer_task_failed", "groups":GROUPS},
            {"id":103, "text":u"爬虫任务", "url":"clawer.views.home.clawer_task", "groups":GROUPS},
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
    failed_reason = models.CharField(max_length=4096, blank=True, null=True)
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
            "failed_reason": self.failed_reason,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result
    
    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
        return ""
    
    def code_dir(self):
        path = os.path.join(settings.MEDIA_ROOT, "codes")
        if os.path.exists(path) is False:
            os.makedirs(path, 0775)
        return path
    
    def alpha_path(self):
        return os.path.join(self.code_dir(), "%d_alpha.py" % self.clawer_id)
    
    def product_path(self):
        return os.path.join(self.code_dir(), "%d_product.py" % self.clawer_id)
    
    @classmethod
    def parse_line(cls, line):
        """ line format is: TASK[\t]uri
        Returns:
            uri
        """
        logging.info("line is: %s", line)
        line = line.strip()
        if not line:
            return None
        tmp = line.split(" ")
        logging.debug("split result is %s", tmp)
        if len(tmp) < 2:
            return None
        if tmp[0] != "TASK":
            return None
        return tmp[1]
    
    def write_code(self, path):
        if os.path.exists(path):
            return
        with codecs.open(path, "w", "utf-8") as f:
            f.write(self.code)
        

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
    store = models.CharField(max_length=4096, blank=True, null=True)
    content_bytes = models.IntegerField(default=0)
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
            "status_name": self.status_name(),
            "content_bytes": self.content_bytes,
            "store": self.store,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "done_datetime": self.done_datetime.strftime("%Y-%m-%d %H:%M:%S") if self.done_datetime else None,
        }
        return result
    
    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
        
        return ""
    
    def store_path(self):
        now = datetime.datetime.now()
        return os.path.join(settings.CLAWER_SOURCE, now.strftime("%Y%m%d"), "%d.txt" % self.id)
