#coding=utf-8
import math
import requests
import logging
import traceback
import subprocess
import time
import rq
import redis
from random import random
import os


from django.conf import settings

from html5helper.utils import do_paginator




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
        args = ["/usr/bin/phantomjs", '--disk-cache=true', '--local-storage-path=/tmp/phantomjs_cache', '--load-images=false']
        
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
    

class UrlCache(object):
    
    def __init__(self, url, redis_url=settings.URL_REDIS):
        self.connection = redis.Redis.from_url(redis_url)
        self.url = "urlcache_%s" %  url or ""
        self.cache_time = 3600*24
        
    def has_url(self):
        if self.connection.get(self.url) > 0:
            return True
        return False
    
    def add_it(self):
        self.connection.set(self.url, 1)
        
    def flush(self):
        self.connection.flushall()
        
    

class DownloadQueue(object):
    QUEUE_NAME = "task_downloader"
    
    def __init__(self, redis_url=settings.REDIS):
        self.connection = redis.Redis.from_url(redis_url)
        self.queue = rq.Queue(self.QUEUE_NAME, connection=self.connection)
        self.jobs = []
        
    def enqueue(self, func, *args, **kwargs):
        job = self.queue.enqueue_call(func, *args, **kwargs)
        self.jobs.append(job)
    

class DownloadWorker(object):
    QUEUE_NAME = "task_downloader"
    
    def __init__(self, redis_url=settings.REDIS):
        self.connection = redis.Redis.from_url(redis_url)
        self.queue = rq.Queue(self.QUEUE_NAME, connection=self.connection)
        self.worker = rq.Worker(self.queue)
        
    def run(self):
        self.worker.work()
    


def download_clawer_task(clawer_task):
    from clawer.models import ClawerTask, ClawerDownloadLog
    
    if clawer_task.status != ClawerTask.STATUS_LIVE:
        return 0
    
    download_log = ClawerDownloadLog(clawer=clawer_task.clawer, task=clawer_task)
    failed = False
    #do download now
    headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0"}
    if clawer_task.cookie:
        headers["cookie"] = clawer_task.cookie
    
    downloader = Download(clawer_task.uri, engine=clawer_task.download_engine if clawer_task.download_engine else Download.ENGINE_REQUESTS)
    #check proxy
    setting = clawer_task.clawer.settings()
    if setting.proxy:
        downloader.add_proxies(setting.proxy.strip().split("\n"))
    downloader.download()
    
    if downloader.failed:
        download_log.status = ClawerDownloadLog.STATUS_FAIL
        download_log.failed_reason = downloader.failed_exception
        download_log.spend_time = int(downloader.spend_time*1000)
        download_log.save()
        clawer_task.status = ClawerTask.STATUS_FAIL
        clawer_task.save()
        return
        
    #save
    try:
        path = clawer_task.store_path()
        if os.path.exists(os.path.dirname(path)) is False:
            os.makedirs(os.path.dirname(path), 0775)
            
        with open(path, "w") as f:
            f.write(downloader.content)
        
        clawer_task.store = path
    except:
        failed = True
        download_log.failed_reason = traceback.format_exc(10)
        
    if failed:
        clawer_task.status = ClawerTask.STATUS_FAIL
        clawer_task.save()
        download_log.status = ClawerDownloadLog.STATUS_FAIL
        download_log.spend_time = int(downloader.spend_time*1000)
        download_log.save()
        return
    
    #update db
    clawer_task.status = ClawerTask.STATUS_SUCCESS
    clawer_task.save()
    
    if downloader.response_headers.get("content-length"):
        download_log.content_bytes = downloader.response_headers["Content-Length"]
    else:
        download_log.content_bytes = len(downloader.content)
    download_log.status = ClawerDownloadLog.STATUS_SUCCESS
    download_log.content_encoding = downloader.content_encoding
    download_log.spend_time = int(downloader.spend_time*1000)
    download_log.save()
    
    return clawer_task.id
