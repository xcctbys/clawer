# coding=utf-8

import json
import traceback
import os
import subprocess
import datetime
import multiprocessing
from optparse import make_option
import sys
import threading
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask,\
    ClawerAnalysisLog


MAX_RUN_TIME = 600


def run(process_number):
    pool = multiprocessing.Pool(process_number)
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    
    #add watcher
    watcher = threading.Timer(MAX_RUN_TIME, force_exit, [pool])
    watcher.start()
    #work
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
            
            pool.apply_async(do_run, (item, ))
        print "clawer %d" % clawer.id
    
    #add watcher 
    pool.close()
    pool.join()
    pool.terminate()
    return True


def force_exit(pool):
    logging.warning("force exit after %d seconds", MAX_RUN_TIME)
    pool.terminate()
    sys.exit(1)


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
    
    print "clawer task %d done" % clawer_task.id    
    

def reset_failed():
    end = datetime.datetime.now() - datetime.timedelta(1)
    start = end - datetime.timedelta(3)
    ClawerTask.objects.filter(status=ClawerTask.STATUS_ANALYSIS_FAIL, done_datetime__range=(start, end)).update(status=ClawerTask.STATUS_SUCCESS)
    


class Command(BaseCommand):
    args = ""
    help = "Analysis clawer download page"
    option_list = BaseCommand.option_list + (
        make_option('--process',
            dest='process',
            default=4,
            help='Pool process number.'
        ),
    )
    
    @wrapper_raven
    def handle(self, *args, **options):
        process_number = int(options["process"])
        run(process_number)