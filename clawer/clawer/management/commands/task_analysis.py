# coding=utf-8

import json
import traceback
import os
import sys
import subprocess
import datetime
import time
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask,\
    ClawerAnalysisLog


def run(runtime, thread_count):
    end = datetime.datetime.now() + datetime.timedelta(seconds=runtime)
    
    while True:
        current = datetime.datetime.now()
        if current >= end:
            sys.exit(1)
            break
        
        if do_run(thread_count) > 0:
            time.sleep(1)
        else:
            time.sleep(5)
        
    return True


def do_run():
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    
    for clawer in clawers:
        analysis = clawer.runing_analysis()
        if not analysis:
            continue
        path = analysis.product_path()
        analysis.write_code(path)
        
        job_count = 0
        clawer_tasks = ClawerTask.objects.filter(clawer_id=clawer.id, status=ClawerTask.STATUS_SUCCESS).order_by("id")[:clawer.settings().analysis]
        for item in clawer_tasks:
            try:
                if os.path.exists(item.store) is False:
                    continue
                do_analysis(item, clawer)
                job_count += 1
            except: 
                print traceback.format_exc(10)   
                
        print "clawer is %d, job count is %d" % (clawer.id, job_count)
    
    return job_count
 

def do_analysis(clawer_task, clawer):
    
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
        make_option('--run',
            dest='run',
            default=300,
            help='Run seconds'
        ),
        make_option('--thread',
            dest='thread',
            default=2,
            help='Run seconds'
        ),
    )
    
    @wrapper_raven
    def handle(self, *args, **options):
        run(int(options["run"]), int(options["thread"]))