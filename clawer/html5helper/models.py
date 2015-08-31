#coding=utf-8

from django.db import models

from html5helper.tasks import write_db
from html5helper.cache import default_cache
        

class BaseModel(models.Model):
    """ Rewrite base class of model. Advise all models to inheritance it.
    """
    class Meta:
        abstract = True
    
    @classmethod
    def get_by_pk(cls, pk, instance=None):
        """ get one object by primary key, will cache
        """
        attr_name = "_%s_cache" % cls.__name__
        if instance and hasattr(instance, attr_name):
            return getattr(instance, attr_name)
        
        key = cls.memcache_key(pk)
        result = default_cache.get(key)
        if result:
            if instance: setattr(instance, attr_name, result)
            return result
        
        result = cls.objects.get(pk=pk)
        if result:
            if instance: setattr(instance, attr_name, result)
            default_cache.set(key, result)
        
        return result
    
    @classmethod
    def memcache_key(cls, pk):
        meta = cls._meta
        return "%s_%s_%s" % (meta.app_label, cls.__name__, pk)
        
    def save(self, **kwargs):
        """ First write to memcached servers, then write to db.
        Kwargs:
            async: Boolean, default is False. You must have django celery installed.
            cache_timeout: Cache in memcached timeout. Unit is second. Default is 300s.
        """
        async = kwargs.pop("async", False)
        cache_timeout = kwargs.pop("cache_timeout", 300)
            
        if async:
            write_db.delay(self, **kwargs)
            return 
    
        self.do_save(**kwargs)
        
        if self.pk:
            default_cache.set(self.memcache_key(self.pk), self, cache_timeout)
        
    def do_save(self, **kwargs):
        super(BaseModel, self).save(**kwargs)
        
    def delete(self, *args, **kwargs):
        key = self.__class__.memcache_key(self.pk)
        default_cache.delete(key)
        super(BaseModel, self).delete(*args, **kwargs)