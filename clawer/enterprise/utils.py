#encoding=utf-8

from enterprise.models import Province

from .libs.beijing_crawler import BeijingCrawler
import urlparse


class EnterpriseDownload(object):
    PROVINCES = [
        {"id": Province.BEIJING, "class": BeijingCrawler}
    ]
    
    def __init__(self, url):
        """ url format:
        enterprise://${province}/${enterprise_name}/${register_no}/?${querystring}
        """
        self.url = url
        
        o = urlparse.urlparse(self.url)
        self.province = o.hostname
        
        tmp = filter(lambda x: x.strip() != "", o.path.split("/"))
        if len(tmp) != 2:
            raise Exception("'%s' format invalid" % self.url)
        
        self.name = tmp[0]
        self.register_no = tmp[1]
        
    def download(self):
        """ Returns: json data
        """
        province_id = Province.to_id(self.province)
        for item in self.PROVINCES:
            if item['id'] != province_id:
                continue
            
            cls = item['class']()
            data = cls.run(self.register_no)
            return data
        
        raise Exception(u"unknown province %s" % self.province)
    