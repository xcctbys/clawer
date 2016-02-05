#encoding=utf-8

from django.db import models


class Province(models.Model):
    name = models.CharField(max_length=128)
    labell = models.CharField(max_length=128)
    add_datetime = models.DateTimeField(auto_now_add=True)
    

class Enterprise(models.Model):
    name = models.CharField(max_length=256)
    province = models.ForeignKey(Province)
    register_no = models.CharField(max_length=128)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    