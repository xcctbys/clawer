#encoding=utf-8

from django.contrib.auth.models import User as DjangoUser
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(DjangoUser)
    nickname = models.CharField(max_length=64)
    
    class Meta:
        app_label = "clawer"