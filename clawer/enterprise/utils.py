#encoding=utf-8
import os

from enterprise.models import Province

from .libs.beijing_crawler import BeijingCrawler
from .libs.chongqing_crawler import ChongqingClawer
from .libs.tianjin_crawler import TianjinCrawler
from .libs.zhejiang_crawler import ZhejiangCrawler
from .libs.shandong_crawler import ShandongCrawler
from .libs.xinjiang_crawler import XinjiangClawer
from .libs.yunnan_crawler import YunnanCrawler
from .libs.neimenggu_crawler import NeimengguClawer

from .libs import settings
import urlparse


class EnterpriseDownload(object):
    PROVINCES = [
        {"id": Province.BEIJING, "class": BeijingCrawler},
        {"id": Province.CHONGQING, "class": ChongqingClawer},
        {"id": Province.TIANJIN, "class": TianjinCrawler},
        {'id': Province.ZHEJIANG, 'class': ZhejiangCrawler},
        {'id': Province.SHANDONG, 'class': ShandongCrawler},
        {'id': Province.XINJIANG, 'class': XinjiangClawer},
        {'id': Province.YUNNAN, 'class': YunnanCrawler},
        {'id': Province.NEIMENGGU, 'class': NeimengguClawer},


    ]

    def __init__(self, url):
        """ url format:
        enterprise://${province}/${enterprise_name}/${register_no}/?${querystring}
        """
        self.url = url
        if os.path.exists(settings.json_restore_path) is False:
            os.makedirs(settings.json_restore_path, 0775)

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

            cls = item['class'](settings.json_restore_path)
            data = cls.run(self.register_no)
            return data

        raise Exception(u"unknown province %s" % self.province)

