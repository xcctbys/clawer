#coding=utf-8

from __future__ import absolute_import

from celery import shared_task

import traceback
import logging
import os
import datetime

from clawer.models import ClawerTask
from clawer.utils import Download


@shared_task
def run_clawer_task(clawer_task):
    if clawer_task.status != ClawerTask.STATUS_LIVE:
        return 0
    
    clawer_task.status = ClawerTask.STATUS_PROCESS
    clawer_task.start_datetime = datetime.datetime.now()
    clawer_task.save()
    
    failed = False
    
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
        clawer_task.status = ClawerTask.STATUS_FAIL
        clawer_task.done_datetime = datetime.datetime.now()
        clawer_task.spend_time = int(downloader.spend_time*1000)
        clawer_task.failed_reason = downloader.failed_exception
        clawer_task.save()
        return
        
    #save
    try:
        path = clawer_task.store_path()
        if os.path.exists(os.path.dirname(path)) is False:
            os.makedirs(os.path.dirname(path), 0775)
            
        with open(path, "w") as f:
            f.write(downloader.content)
    except:
        logging.warning(traceback.format_exc(10))
        failed = True
        clawer_task.failed_reason = traceback.format_exc(10)
        
    if failed:
        clawer_task.status = ClawerTask.STATUS_FAIL
        clawer_task.done_datetime = datetime.datetime.now()
        clawer_task.spend_time = int(downloader.spend_time*1000)
        clawer_task.save()
        return
    
    #update db
    clawer_task.status = ClawerTask.STATUS_SUCCESS
    if downloader.response_headers.get("content-length"):
        clawer_task.content_bytes = downloader.response_headers["Content-Length"]
    else:
        clawer_task.content_bytes = len(downloader.content)
    clawer_task.content_encoding = downloader.content_encoding
    clawer_task.store = path
    clawer_task.done_datetime = datetime.datetime.now()
    clawer_task.spend_time = int(downloader.spend_time*1000)
    clawer_task.save()
    
    return clawer_task.id


