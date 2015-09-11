# coding=utf-8

import json
import traceback
import threadpool
import os
import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator, Clawer, ClawerTask,\
    ClawerAnalysisLog, ClawerAnalysis



def run():
    pool = threadpool.ThreadPool(5)
    #scan tasks
    need_analysis_tasks = []
    clawer_tasks = ClawerTask.objects.filter(clawer__status=Clawer.STATUS_ON, status=ClawerTask.STATUS_SUCCESS)[:100]
    for item in clawer_tasks:
        
        if os.path.exists(item.store) is False:
            continue
        need_analysis_tasks.append(item)
        
    requests = threadpool.makeRequests(do_run, need_analysis_tasks)
    [pool.putRequest(x, timeout=300) for x in requests]
    pool.wait()
    return True


def do_run(clawer_task):
    clawer = clawer_task.clawer
    
    analysis = clawer.runing_analysis()
    path = analysis.product_path()
    analysis.write_code(path)
    
    analysis_log = ClawerAnalysisLog(clawer=clawer, analysis=analysis, task=clawer_task)
    
    try:
        p = subprocess.Popen([settings.PYTHON, path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #("%s %s" % (settings.PYTHON, path), "r")
        #write path to it
        p.stdin.write(json.dumps({"path": clawer_task.store}))
        #read from stdout, stderr
        analysis_log.result = p.stdout.read()
        err = p.stderr.read()
        
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
    return analysis_log    
    
    


class Command(BaseCommand):
    args = ""
    help = "Analysis clawer download page"
    
    @wrapper_raven
    def handle(self, *args, **options):
        run()