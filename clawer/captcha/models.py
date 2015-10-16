#encoding=utf-8

from django.db import models
from django.conf import settings
import urlparse

# Create your models here.


class Captcha(models.Model):
    url = models.URLField()
    category = models.IntegerField()
    image_hash = models.CharField(max_length=32)
    label_count = models.IntegerField(default=0)
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "captcha"
    
    def image_url(self):
        return urlparse.urljoin(settings.MEDIA_URL, "captcha/%d/%s" % (self.category, self.image_hash))
        
        
class LabelLog(models.Model):
    captcha = models.ForeignKey(Captcha)
    label = models.CharField(max_length=32)
    ip = models.IPAddressField()
    add_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "captcha"
        
        