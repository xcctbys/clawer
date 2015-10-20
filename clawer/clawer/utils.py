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
import types
import socket
import urlparse
import shutil
import os

from django.conf import settings

from html5helper.utils import do_paginator
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import threading




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
    ENGINE_SELENIUM = "selenium"
    
    ENGINE_CHOICES = (
        (ENGINE_REQUESTS, "REQUESTS"),
        (ENGINE_PHANTOMJS, "PHANTOMJS"),
        (ENGINE_SELENIUM, "SELENIUM"),
    )
    
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
        
    def add_headers(self, headers):
        self.headers.update(headers)
        
    def download(self):
        if self.engine == self.ENGINE_REQUESTS:
            self.download_with_requests()
        elif self.engine == self.ENGINE_PHANTOMJS:
            self.download_with_phantomjs()
        elif self.engine == self.ENGINE_SELENIUM:
            self.download_with_selenium()
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
        
    def download_with_selenium(self):
        from selenium import webdriver
        
        start = time.time()
        
        firefox_log_file = open("/tmp/firefox.log", "a+")
        firefox_binary = FirefoxBinary(log_file=firefox_log_file)
        driver = webdriver.Firefox(firefox_binary=firefox_binary)
        driver.set_page_load_timeout(30)
        
        try:
            driver.get(self.url)
            self.content = driver.execute_script("return document.documentElement.outerHTML;")
        except:
            self.failed_exception = traceback.format_exc(10)
            self.failed = True
        finally:
            driver.close()
            driver.quit()
        #remove files
        try:
            if os.path.exists(driver.profile.path):
                shutil.rmtree(driver.profile.path)
            if driver.profile.tempfolder is not None:
                shutil.rmtree(driver.profile.tempfolder)
        except:
            logging.error(traceback.format_exc(10))
    
        end = time.time()
        self.spend_time = end - start


class SafeProcess(object):
    
    def __init__(self, args, stdout=None, stderr=None, stdin=None):
        self.args = args
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.process = None
        self.timer = None
        self.process_exit_status = None
        self.timeout = 0
        
    def run(self, timeout=30):
        self.timeout = timeout
        self.timer = threading.Timer(timeout, self.force_exit)
        self.timer.start()
        
        self.process = subprocess.Popen(self.args, stdout=self.stdout, stderr=self.stderr, stdin=self.stdin)
        return self.process
    
    def wait(self):
        self.process_exit_status = self.process.wait()
        self.timer.cancel()   
        return self.process_exit_status
    
    def force_exit(self):
        if not self.timer:
            return
        
        if self.timer.is_alive() and self.process:
            if self.process.stdout:
                self.process.stdout.write("timeout after %d seconds" % self.timeout)
            self.process.terminate()
            
        self.process_exit_status = 1
    
        
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
        self.connection.setex(self.url, self.cache_time, 1)
        
    def flush(self):
        self.connection.flushall()
        
    

class DownloadQueue(object):
    QUEUE_NAME = "task_downloader"
    URGENCY_QUEUE_NAME = "urgency_task_downloader"
    MAX_COUNT = 10000
    
    def __init__(self, is_urgency=False, redis_url=settings.REDIS):
        self.connection = redis.Redis.from_url(redis_url)
        self.queue = rq.Queue(self.QUEUE_NAME, connection=self.connection)
        self.urgency_queue = rq.Queue(self.URGENCY_QUEUE_NAME, connection=self.connection)
        self.is_urgency = is_urgency
        self.jobs = []
        
    def enqueue(self, func, *args, **kwargs):
        job = None
        if self.is_urgency:
            if self.urgency_queue.count > self.MAX_COUNT:
                return None
            job = self.urgency_queue.enqueue_call(func, *args, **kwargs)
        else:
            if self.queue.count > self.MAX_COUNT:
                return None
            job = self.queue.enqueue_call(func, *args, **kwargs)
        
        self.jobs.append(job)
        return job.id
    

class DownloadWorker(object):
    QUEUE_NAME = DownloadQueue.QUEUE_NAME
    URGENCY_QUEUE_NAME = DownloadQueue.URGENCY_QUEUE_NAME
    
    def __init__(self, redis_url=settings.REDIS):
        self.connection = redis.Redis.from_url(redis_url)
        
        self.queue = rq.Queue(self.QUEUE_NAME, connection=self.connection)
        self.worker = rq.Worker(self.queue)
        
        self.urgency_queue = rq.Queue(self.URGENCY_QUEUE_NAME, connection=self.connection)
        self.urgency_worker = rq.Worker(self.urgency_queue)
        
    def run(self):
        self.worker.work()
        
    def urgency_run(self):
        self.urgency_worker.work()
        

class DownloadClawerTask(object):
    
    def __init__(self, clawer_task):
        from clawer.models import ClawerDownloadLog, RealTimeMonitor
        
        self.clawer_task = clawer_task
        self.download_log = ClawerDownloadLog(clawer=clawer_task.clawer, task=clawer_task, hostname=socket.gethostname())
        self.monitor = RealTimeMonitor()
        self.headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0"}
        
        self.clawer_setting = self.clawer_task.clawer.cached_setting()
        
        self.downloader = Download(self.clawer_task.uri, engine=self.clawer_setting.download_engine)
        if self.clawer_setting.proxy:
            self.downloader.add_proxies(self.clawer_setting.proxy.strip().split("\n"))
        if self.clawer_task.cookie:
            self.headers["cookie"] = self.clawer_task.cookie
            self.downloader.add_cookie(self.clawer_task.cookie)
        self.downloader.add_headers(self.headers)
        
    def download(self):
        from clawer.models import ClawerTask, ClawerDownloadLog
    
        if not self.clawer_task.status in [ClawerTask.STATUS_LIVE, ClawerTask.STATUS_PROCESS]:
            return 0
        
        failed = False
        
        self.downloader.download()
        
        if self.downloader.failed:
            self.download_failed()
            return 0
            
        #save
        try:
            path = self.clawer_task.store_path()
            if os.path.exists(os.path.dirname(path)) is False:
                os.makedirs(os.path.dirname(path), 0775)
                
            with open(path, "w") as f:
                content = self.downloader.content
                if isinstance(content, types.UnicodeType):
                    content = content.encode("utf-8")
                f.write(content)
            
            self.clawer_task.store = path
        except:
            failed = True
            self.download_log.failed_reason = traceback.format_exc(10)
            
        if failed:
            self.download_failed()
            return 0
        
        #success handle
        self.clawer_task.status = ClawerTask.STATUS_SUCCESS
        self.clawer_task.save()
        
        if self.downloader.response_headers.get("content-length"):
            self.download_log.content_bytes = self.downloader.response_headers["Content-Length"]
        else:
            self.download_log.content_bytes = len(self.downloader.content)
        self.download_log.status = ClawerDownloadLog.STATUS_SUCCESS
        self.download_log.content_encoding = self.downloader.content_encoding
        self.download_log.spend_time = int(self.downloader.spend_time*1000)
        self.download_log.save()
        
        self.monitor.trace_task_status(self.clawer_task)
        return self.clawer_task.id
        
    def download_failed(self):
        from clawer.models import ClawerTask, ClawerDownloadLog
        
        self.download_log.status = ClawerDownloadLog.STATUS_FAIL
        if self.downloader.failed_exception:
            self.download_log.failed_reason = self.downloader.failed_exception
        self.download_log.spend_time = int(self.downloader.spend_time*1000)
        self.download_log.save()
        
        self.clawer_task.status = ClawerTask.STATUS_FAIL
        self.clawer_task.save()
        
        self.monitor.trace_task_status(self.clawer_task)
    

def download_clawer_task(clawer_task):
    downloader = DownloadClawerTask(clawer_task)
    ret = downloader.download()
    return ret
    
