#coding=utf-8
import math
import requests
import logging
import traceback
import subprocess
import time

from django.conf import settings

from html5helper.utils import do_paginator
from random import random




def check_auth_for_api(view_func):
    """ mobile GET must have secret="", return dict
    """
    def wrap(request, *args, **kwargs):
        if request.user and request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        
        login_error = {"is_ok":False, "reason":u"登陆凭证已经失效，请重新登陆", "login_timeout":True}
        return login_error
    return wrap
    

class EasyUIPager(object):
    
    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request
        
    def query(self):
        """ return dict
        """
        page = int(self.request.GET.get("page", '1'))
        rows = int(self.request.GET.get("rows", '20'))
        sort = self.request.GET.get("sort", "id")
        order = self.request.GET.get("order", "desc")
        
        result = {"is_ok":True, "rows":[], "total":0, "page": page, "total_page":0}
        
        def get_order(o):
            return "" if o == "asc" else "-"
        
        qs = self.queryset
        if sort:
            items = qs.order_by("%s%s" % (get_order(order), sort))
        else:
            items = qs
        pager = do_paginator(items, page, rows)
        result["total"] = pager.paginator.count
        result["rows"] = [x.as_json() for x in pager]
        result["total_page"] = math.ceil(float(result["total"])/rows)
        
        return result
        

class Download(object):
    ENGINE_REQUESTS = "requests"
    ENGINE_PHANTOMJS = "phantomjs"
    
    def __init__(self, url, engine=ENGINE_REQUESTS):
        self.engine = engine
        self.url = url
        self.spend_time = 0  #unit is million second
        self.cookie = ""
        self.content = None
        self.failed_exception = None
        self.content_encoding = None
        self.failed = False
        self.headers = {}
        self.response_headers = {}
        self.proxies = []
        
    def add_cookie(self, cookie):
        self.headers["Cookie"] = cookie
        
    def add_proxies(self, proxies):
        self.proxies = proxies
        
    def download(self):
        if self.engine == self.ENGINE_REQUESTS:
            self.download_with_requests()
        elif self.engine == self.ENGINE_PHANTOMJS:
            self.download_with_phantomjs()
        else:
            self.download_with_phantomjs()
    
    def download_with_requests(self):
        r = None
        start = time.time()
        
        try:
            r = requests.get(self.url, headers=self.headers, proxies=self.proxies)
        except:
            self.failed = True
            self.failed_exception = traceback.format_exc(10)
            logging.warning(self.failed_exception)
        
        if self.failed:
            end = time.time()
            self.spend_time = end - start
            return
        
        self.response_headers = r.headers
        self.content = r.content
        self.content_encoding = r.encoding
        end = time.time()
        self.spend_time = end - start
    
    def download_with_phantomjs(self):
        start = time.time()
        args = ["/usr/bin/phantomjs"]
        if len(self.proxies) > 1:
            proxy = self.proxies[random.randint(0, len(self.proxies) - 1)]
            args.append("--proxy=%s" % proxy)
        args += [settings.DOWNLOAD_JS, self.url]
        if "Cookie" in self.headers:
            args.append(self.headers["Cookie"])

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #("%s %s" % (settings.PYTHON, path), "r")
        self.content = p.stdout.read()
        self.failed_exception = p.stderr.read()
        status = p.wait()
        
        end = time.time()
        self.spend_time = end - start
        
        if status != 0:
            self.failed = True    
            return
        
        