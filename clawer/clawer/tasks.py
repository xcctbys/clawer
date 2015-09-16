#coding=utf-8

from __future__ import absolute_import

from celery import shared_task

import traceback
import requests
import logging
import os
import datetime
import time
import codecs

from clawer.models import ClawerTask


@shared_task
def run_clawer_task(clawer_task):
    if clawer_task.status != ClawerTask.STATUS_LIVE:
        return 0
    
    start = time.time()
    clawer_task.status = ClawerTask.STATUS_PROCESS
    clawer_task.start_datetime = datetime.datetime.now()
    clawer_task.save()
    
    failed = False
    r = None
    
    headers = {"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0"}
    if clawer_task.cookie:
        headers["cookie"] = clawer_task.cookie
    
    try:
        r = requests.get(clawer_task.uri, headers=headers)
    except:
        logging.warning(traceback.format_exc(10))
        failed = True
    
    if r.status_code != 200:
        failed = True
        
    if failed:
        clawer_task.status = ClawerTask.STATUS_FAIL
        clawer_task.done_datetime = datetime.datetime.now()
        clawer_task.spend_time = int((time.time() - start)*1000)
        clawer_task.save()
        return
        
    #save
    try:
        path = clawer_task.store_path()
        if os.path.exists(os.path.dirname(path)) is False:
            os.makedirs(os.path.dirname(path), 0775)
            
        with open(path, "w") as f:
            f.write(r.content)
    except:
        logging.warning(traceback.format_exc(10))
        failed = True
        
    if failed:
        clawer_task.status = ClawerTask.STATUS_FAIL
        clawer_task.done_datetime = datetime.datetime.now()
        clawer_task.spend_time = int((time.time() - start)*1000)
        clawer_task.save()
        return
    
    #update db
    clawer_task.status = ClawerTask.STATUS_SUCCESS
    if r.headers.get("content-length"):
        clawer_task.content_bytes = r.headers["Content-Length"]
    else:
        clawer_task.content_bytes = len(r.content)
    clawer_task.content_encoding = r.encoding
    clawer_task.store = path
    clawer_task.done_datetime = datetime.datetime.now()
    clawer_task.spend_time = int((time.time() - start)*1000)
    clawer_task.save()
    
    return clawer_task.id


