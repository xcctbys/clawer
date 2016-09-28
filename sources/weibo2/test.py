#!/usr/local/bin/python
#encoding=utf-8
import urlparse
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Generator(object):
    def __init__(self):
        self.HOST = "http://m.weibo.cn/page/pageJson"
    def pack_url(self, keyword='医疗', page=1):
        qs = {
            "containerid":"",
            "containerid": (u"100103type=1&q=%s" % keyword).encode("utf-8"),
            "ext":"",
            "fid": (u"100103type=1&q=%s" % keyword).encode("utf-8"),
            "uicode": "10000011",
            "v_p":"11",
            "type":"all",
            "queryVal": keyword.encode("utf-8"),
            "page": page
        }
        print urlparse.urljoin(self.HOST, "?%s" % urllib.urlencode(qs))
        return urlparse.urljoin(self.HOST, "?%s" % urllib.urlencode(qs))

if __name__=='__main__':
    g = Generator()
    g.pack_url()