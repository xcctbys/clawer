#encoding=utf-8
import copy
import os
import logging
import datetime
import codecs
import redis

from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.conf import settings
import json
from clawer.utils import Download, UrlCache
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from html5helper import redis_cluster
import urlparse

        

class Clawer(models.Model):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线"),
    )
    name = models.CharField(max_length=128)
    info = models.CharField(max_length=1024)
    customer = models.CharField(max_length=128, blank=True, null=True)
    status = models.IntegerField(default=STATUS_ON, choices=STATUS_CHOICES)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        
    def as_json(self):
        result = {"id": self.id,
            "name": self.name,
            "info": self.info,
            "customer": self.customer,
            "status": self.status,
            "status_name": self.status_name(),
            "result_url": self.result_url(),
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        runing =  self.runing_task_generator()
        result["runing_task_generator"] = runing.as_json() if runing else None
            
        analysis = self.runing_analysis()
        result["runing_analysis"] = analysis.as_json() if analysis else None
        
        result["setting"] = self.settings().as_json()
        
        return result
    
    def runing_task_generator(self):
        try:
            result = ClawerTaskGenerator.objects.filter(clawer=self, status=ClawerTaskGenerator.STATUS_ON)[0]
        except:
            result = None
        
        return result
    
    def runing_analysis(self):
        try:
            result = ClawerAnalysis.objects.filter(clawer=self, status=ClawerAnalysis.STATUS_ON)[0]
        except:
            result = None
        
        return result
    
    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
            
        return ""
    
    def settings(self):
        return ClawerSetting.objects.get_or_create(clawer=self)[0]
    
    def result_url(self):
        return urlparse.urljoin(settings.CLAWER_RESULT_URL, "%d" % self.id)
        
        
class ClawerAnalysis(models.Model):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_ON, u"启用"),
        (STATUS_OFF, u"下线"),
    )
    clawer = models.ForeignKey(Clawer)
    code = models.TextField()  #python code
    status = models.IntegerField(default=STATUS_ON, choices=STATUS_CHOICES)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        
    def as_json(self):
        result = {"id": self.id,
            "code": self.code,
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
    
    def code_dir(self):
        path = os.path.join(settings.MEDIA_ROOT, "codes")
        if os.path.exists(path) is False:
            os.makedirs(path, 0775)
        return path
    
    def product_path(self):
        return os.path.join(self.code_dir(), "%d_analysis.py" % self.clawer_id)
    
    def write_code(self, path):
        if os.path.exists(path):
            os.remove(path)
        with codecs.open(path, "w", "utf-8") as f:
            f.write(self.code)
    

class ClawerAnalysisLog(models.Model):
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    clawer = models.ForeignKey(Clawer)
    analysis = models.ForeignKey(ClawerAnalysis)
    task = models.ForeignKey('ClawerTask')
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    failed_reason = models.CharField(max_length=1024, null=True, blank=True)
    hostname = models.CharField(null=True, blank=True, max_length=16)
    result = models.TextField(null=True, blank=True)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        
    def as_json(self):
        result = {"id":self.id,
            "clawer": self.clawer.as_json(),
            "analysis": self.analysis.as_json(),
            "task": self.task.as_json(),
            "status": self.status,
            "status_name": self.status_name(),
            "failed_reason": self.failed_reason,
            "result": self.result,
            "hostname": self.hostname,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result
    
    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
            
        return ""
    
    def result_path(self):
        parent = os.path.join("/tmp", "clawer_analysis")
        if os.path.exists(parent) is False:
            os.mkdir(parent)
        return os.path.join(parent, "%d.analysis" % self.task.id)
    

class ClawerDownloadLog(models.Model):
    (STATUS_FAIL, STATUS_SUCCESS) = range(1, 3)
    STATUS_CHOICES = (
        (STATUS_FAIL, u"失败"),
        (STATUS_SUCCESS, u"成功"),
    )
    clawer = models.ForeignKey(Clawer)
    task = models.ForeignKey('ClawerTask')
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    failed_reason = models.CharField(max_length=1024, null=True, blank=True)
    content_bytes = models.IntegerField(default=0)
    content_encoding = models.CharField(null=True, blank=True, max_length=32)
    hostname = models.CharField(null=True, blank=True, max_length=16)
    spend_time = models.IntegerField(default=0) #unit is microsecond
    add_datetime = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = "clawer"
        
    def as_json(self):
        result = {"id":self.id,
            "clawer": self.clawer.as_json(),
            "task": self.task.as_json(),
            "status": self.status,
            "status_name": self.status_name(),
            "hostname": self.hostname,
            "failed_reason": self.failed_reason,
            "content_bytes": self.content_bytes,
            "content_encoding": self.content_encoding,
            "spend_time": self.spend_time,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result
    
    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
            
        return ""
    

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
        """ line format is: {"uri":""}
        Returns:
            dict of json
        """
        logging.info("line is: %s", line)
        js = json.loads(line)
        return js
    
    def write_code(self, path):
        with codecs.open(path, "w", "utf-8") as f:
            f.write(self.code)




class LoggerCategory(object):
    ADD_TASK = u"手工增加任务"
    UPDATE_TASK_GENERATOR  = u"更新任务生成器"
    UPDATE_ANALYSIS = u"更新分析器"
    UPDATE_SETTING = u"更新爬虫参数"
    TASK_ANALYSIS_FAILED_RESET = u"重设分析失败的任务"
    
    

class Logger(models.Model):
    """用户操作记录表
    """
    user = models.ForeignKey(DjangoUser, blank=True, null=True)
    category = models.CharField(max_length=64)
    title = models.CharField(max_length=512)
    content = models.TextField() # must is json format
    from_ip = models.IPAddressField()
    add_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = "clawer"
        
        
    def as_json(self):
        result = { "id": self.id,
            "user_id": self.user_id if self.user else 0,
            "user_profile": self.user.get_profile().as_json() if self.user else None,
            "category": self.category,
            "title": self.title,
            "content": self.content,
            "from_ip": self.from_ip,
            "add_at": self.add_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result
        

class ClawerTask(models.Model):
    (STATUS_LIVE, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS, STATUS_ANALYSIS_FAIL, STATUS_ANALYSIS_SUCCESS) = range(1, 7)
    STATUS_CHOICES = (
        (STATUS_LIVE, u"新增"),
        (STATUS_PROCESS, u"进行中"),
        (STATUS_FAIL, u"下载失败"),
        (STATUS_SUCCESS, u"下载成功"),
        (STATUS_ANALYSIS_FAIL, u"分析失败"),
        (STATUS_ANALYSIS_SUCCESS, u"分析成功"),
    )
    clawer = models.ForeignKey(Clawer)
    task_generator = models.ForeignKey(ClawerTaskGenerator, blank=True, null=True)
    uri = models.CharField(max_length=1024)
    cookie = models.CharField(max_length=1024, blank=True, null=True)
    status = models.IntegerField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    store = models.CharField(max_length=512, blank=True, null=True)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        ordering = ["-id"]
        
    def as_json(self):
        result = {"id":self.id,
            "clawer": self.clawer.as_json(),
            "task_generator": self.task_generator.as_json() if self.task_generator else None,
            "uri": self.uri,
            'cookie': self.cookie,
            "status": self.status,
            "status_name": self.status_name(),
            "store": self.store,
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result
    
    def status_name(self):
        for item in self.STATUS_CHOICES:
            if item[0] == self.status:
                return item[1]
        
        return ""
    
    def store_path(self):
        now = datetime.datetime.now()
        return os.path.join(settings.CLAWER_SOURCE, now.strftime("%Y/%m/%d"), "%d.txt" % self.id)

    

class ClawerSetting(models.Model):
    clawer = models.ForeignKey(Clawer)
    dispatch = models.IntegerField(u"每次分发下载任务数", default=100)
    analysis = models.IntegerField(u"每次分析任务数", default=20)
    proxy = models.TextField(blank=True, null=True)
    download_engine = models.CharField(max_length=16, default=Download.ENGINE_REQUESTS, choices=Download.ENGINE_CHOICES)
    last_update_datetime = models.DateTimeField(auto_now_add=True, auto_now=True)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        ordering = ["-id"]
        
    def as_json(self):
        result = {
            "dispatch": self.dispatch,
            "analysis": self.analysis,
            "proxy": self.proxy or "",
            "download_engine": self.download_engine,
            "last_update_datetime": self.last_update_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "add_datetime": self.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return result
    

class RealTimeMonitor(object):
    POINT_COUNT = 24*60
    
    def __init__(self, redis_url=settings.MONITOR_REDIS):
        self.redis = redis_cluster.PickledRedis.from_url(redis_url)
        
    def load_task_stat(self, status):
        result = {}
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        in_data = self.redis.get(self.task_key(status))
        if in_data and len(in_data["data"].keys()) >= self.POINT_COUNT:
            result = in_data
        else:
            result = {"end_datetime": now, 
                "data":{}
            }
            for i in range(self.POINT_COUNT):
                t = result["end_datetime"] - datetime.timedelta(minutes=i)
                result["data"][t] = {"count": 0}
        
        if result["end_datetime"] != now:
            old_end = result["end_datetime"]
            dts = sorted(result["data"].keys())
            offset = int((now - old_end).total_seconds()/60)
            for i in range(offset):
                dt = old_end + datetime.timedelta(minutes=i+1)
                result["data"][dt] = {"count":0}
                #remove too old
                if i < len(dts):
                    del result["data"][dts[i]]
            
        
        logging.debug("result is: %s", result)
        return result
    
    def task_key(self, status):
        return "realtime_monitor_task_%d" % status
    
    def task_incr_key(self, status):
        return "realtime_monitor_task_incr_%d" % status
    
    def trace_task_status(self, clawer_task):
        result = self.load_task_stat(clawer_task.status)
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        result["end_datetime"] = now
        old = result["data"].get(now)
        if old:
            old["count"] += 1
        else:
            result["data"][now] = {"count":1}
        
        #remove first if time go
        dts = result["data"].keys()
        if len(dts) > self.POINT_COUNT:
            last = sorted(dts)[0]
            assert last != now
            del result["data"][last]
            
        self.redis.set(self.task_key(clawer_task.status), result)
        self.redis.incr(self.task_incr_key(clawer_task.status))
        
        logging.debug("trace task %d, status %s, count is %d", clawer_task.id, clawer_task.status_name(), result["data"][now]["count"])
        return result
    
    



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
            {"id":101, "text":u"爬虫代码配置", "url":"clawer.views.home.clawer_all", "groups":GROUPS},
            {"id":103, "text":u"爬虫任务", "url":"clawer.views.home.clawer_task", "groups":GROUPS},
            {"id":102, "text":u"爬虫下载日志", "url":"clawer.views.home.clawer_download_log", "groups":GROUPS},
            {"id":104, "text":u"爬虫分析日志", "url":"clawer.views.home.clawer_analysis_log", "groups":GROUPS},
            {"id":105, "text":u"数据下载", "url":settings.MEDIA_URL, "groups":GROUPS},
        ]},
        {"id":3, "text": u"实时监控", "url":"", "children": [
            {"id":101, "text":u"实时Dashboard", "url":"clawer.views.monitor.realtime_dashboard", "groups":GROUPS},
        ]},
        
        {"id":2, "text": u"系统管理", "url":"", "children": [
            {"id":201, "text":u"爬虫参数", "url":"clawer.views.home.clawer_setting", "groups":[GROUP_MANAGER]},
            {"id":201, "text":u"操作日志", "url":"clawer.views.logger.index", "groups":[GROUP_MANAGER]},
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
                    try:
                        if menu["url"]:
                            new_menu["url"] = reverse(menu["url"])
                    except:
                        new_menu["url"] = menu["url"]
                        
                    del new_menu["groups"]
                    new_item["children"].append(new_menu)
            menus.append(new_item)
        
        return menus
