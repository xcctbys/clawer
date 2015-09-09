#coding=utf-8

from __future__ import absolute_import

from celery import shared_task

import traceback
import requests
import logging
import os

from clawer.models import ClawerTask


@shared_task
def run_clawer_task(clawer_task):
    if clawer_task.status != ClawerTask.STATUS_LIVE:
        return 0
    
    clawer_task.status = ClawerTask.STATUS_PROCESS
    clawer_task.save()
    failed = False
    
    try:
        r = requests.get(clawer_task.uri)
        if r.status_code != 200:
            clawer_task.status = ClawerTask.STATUS_FAIL
            clawer_task.save()
            return 0
    except:
        logging.warning(traceback.format_exc(10))
        failed = True
        
    if failed:
        clawer_task.status = ClawerTask.STATUS_FAIL
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
        clawer_task.save()
        return
    
    #update db
    clawer_task.status = ClawerTask.STATUS_SUCCESS
    if r.headers.get("content-length"):
        clawer_task.content_bytes = r.headers["Content-Length"]
    else:
        clawer_task.content_bytes = len(r.content)
    clawer_task.store = path
    clawer_task.save()
    
    return clawer_task.id


