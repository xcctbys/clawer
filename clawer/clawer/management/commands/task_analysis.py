# coding=utf-8

import json
import traceback
import threadpool
import os
import subprocess
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask,\
    ClawerAnalysisLog



def run():
    pool = threadpool.ThreadPool(4)
    
    need_analysis_tasks = []
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    for clawer in clawers:
        analysis = clawer.runing_analysis()
        if not analysis:
            continue
        path = analysis.product_path()
        analysis.write_code(path)
        
        clawer_tasks = ClawerTask.objects.filter(clawer_id=clawer.id, status=ClawerTask.STATUS_SUCCESS).order_by("id")[:clawer.settings().analysis]
        for item in clawer_tasks:
            if os.path.exists(item.store) is False:
                continue
            need_analysis_tasks.append(item)
        
    requests = threadpool.makeRequests(do_run, need_analysis_tasks)
    [pool.putRequest(x, timeout=120) for x in requests]
    pool.wait()
    #reset failed task
    #reset_failed()
    return True


def do_run(clawer_task):
    clawer = clawer_task.clawer
    
    analysis = clawer.runing_analysis()
    if not analysis:
        return None
    path = analysis.product_path()
    
    analysis_log = ClawerAnalysisLog(clawer=clawer, analysis=analysis, task=clawer_task)
    
    try:
        p = subprocess.Popen([settings.PYTHON, path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #("%s %s" % (settings.PYTHON, path), "r")
        #write path to it
        p.stdin.write(json.dumps({"path":clawer_task.store, "url":clawer_task.uri}))
        p.stdin.close()
        #read from stdout, stderr
        err = p.stderr.read()
        if not err:
            result = json.loads(p.stdout.read())
            result["_url"] = clawer_task.uri
            if clawer_task.cookie:
                result["_cookie"] = clawer_task.cookie
            analysis_log.result = json.dumps(result)
        
        status = p.wait()
        if status != 0:
            analysis_log.status = ClawerAnalysisLog.STATUS_FAIL
            analysis_log.failed_reason = err
        else:
            analysis_log.status = ClawerAnalysisLog.STATUS_SUCCESS
            
    except:
        analysis_log.failed_reason = traceback.format_exc(10)
        analysis_log.status = ClawerAnalysisLog.STATUS_FAIL
        
    analysis_log.save()
    #update clawer task status
    if analysis_log.status == ClawerAnalysisLog.STATUS_SUCCESS:
        clawer_task.status = ClawerTask.STATUS_ANALYSIS_SUCCESS
    elif analysis_log.status == ClawerAnalysisLog.STATUS_FAIL:
        clawer_task.status = ClawerTask.STATUS_ANALYSIS_FAIL
    clawer_task.save()
    
    return analysis_log    
    

def reset_failed():
    end = datetime.datetime.now() - datetime.timedelta(1)
    start = end - datetime.timedelta(3)
    ClawerTask.objects.filter(status=ClawerTask.STATUS_ANALYSIS_FAIL, done_datetime__range=(start, end)).update(status=ClawerTask.STATUS_SUCCESS)
    


class Command(BaseCommand):
    args = ""
    help = "Analysis clawer download page"
    
    @wrapper_raven
    def handle(self, *args, **options):
        run()