#coding=utf-8
import datetime

from django.contrib.auth.models import User
from django.core.cache import cache

from html5helper.models import BaseModel


class DjUser(User, BaseModel):
    class Meta:
        proxy = True
            
    def profile(self):
        if hasattr(self, "_profile") and self._profile:
            return self._profile
        # check memcached
        cls = self.__class__
        key = "%s_%s_profile_%s" % (cls._meta.app_label, cls.__name__, self.pk)
        self._profile = cache.get(key)
        if self._profile:
            return self._profile
        
        self._profile = self.get_profile()
        if self._profile:
            cache.set(key, self._profile, 3600)

        return self._profile
    
    def psychological_resume(self):
        from psychological.models import Resume
        return Resume.get_by_pk(self.pk, self)
    
    def is_fresh(self):
        now = datetime.datetime.now()
        if (now - self.date_joined).total_seconds() > 3600*72:
            return False
        return True