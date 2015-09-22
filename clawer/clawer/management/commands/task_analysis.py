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



def run(process_number, run_time):
    pool = multiprocessing.Pool(process_number)
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    
    #add watcher
    watcher = threading.Timer(run_time, force_exit, [pool])
    watcher.start()
    
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
            pool.apply_async(do_run, [item])
        print "clawer is %d" % clawer.id
    
    pool.close()
    pool.join()
    return True


def force_exit(pool):
    print "force exit after run"
    pool.terminate()
    sys.exit(0)
    

def do_run(clawer_task):
    clawer = clawer_task.clawer
    
    analysis = clawer.runing_analysis()
    path = analysis.product_path()
    
    analysis_log = ClawerAnalysisLog(clawer=clawer, analysis=analysis, task=clawer_task)
    
    try:
        out_f = open(analysis_log.result_path(), "w+b")
        p = subprocess.Popen([settings.PYTHON, path], stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=out_f)
        p.stdin.write(json.dumps({"path":clawer_task.store, "url":clawer_task.uri}))
        p.stdin.close()
        
        err = p.stderr.read()
        print "waiting analysis return, task %d" % clawer_task.id
        retcode = p.wait()
        if retcode == 0:
            print "out file point %d" % out_f.tell()
            out_f.seek(0)
            result = json.loads(out_f.read())
            result["_url"] = clawer_task.uri
            if clawer_task.cookie:
                result["_cookie"] = clawer_task.cookie
            analysis_log.result = json.dumps(result)
            analysis_log.status = ClawerAnalysisLog.STATUS_SUCCESS
        else:
            analysis_log.status = ClawerAnalysisLog.STATUS_FAIL
            analysis_log.failed_reason = err
            
        out_f.close()
        os.remove(analysis_log.result_path()) 
    except:
        analysis_log.status = ClawerAnalysisLog.STATUS_FAIL
        analysis_log.failed_reason = traceback.format_exc(10)
        
    analysis_log.save()
    #update clawer task status
    if analysis_log.status == ClawerAnalysisLog.STATUS_SUCCESS:
        clawer_task.status = ClawerTask.STATUS_ANALYSIS_SUCCESS
    elif analysis_log.status == ClawerAnalysisLog.STATUS_FAIL:
        clawer_task.status = ClawerTask.STATUS_ANALYSIS_FAIL
    clawer_task.save()
    
    print "clawer task %d done" % clawer_task.id
    return analysis_log



class Command(BaseCommand):
    args = ""
    help = "Analysis clawer download page"
    option_list = BaseCommand.option_list + (
        make_option('--process',
            dest='process',
            default=4,
            help='Pool process number.'
        ),
        make_option('--run',
            dest='run',
            default=300,
            help='Run seconds'
        ),
    )
    
    @wrapper_raven
    def handle(self, *args, **options):
        process_number = int(options["process"])
        run_time = int(options["run"])
        run(process_number, run_time)