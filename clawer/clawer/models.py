#encoding=utf-8

from django.contrib.auth.models import User as DjangoUser
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(DjangoUser)
    nickname = models.CharField(max_length=64)
    
    class Meta:
        app_label = "clawer"
        

class Clawer(models.Model):
    name = models.CharField(max_length=128)
    info = models.CharField(max_length=1024)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "clawer"
        

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
        
