# coding=utf-8

import traceback
import os
import datetime
import multiprocessing
from optparse import make_option
import sys
import threading

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask,\
    ClawerDownloadLog
from clawer.utils import Download



def run(process_number, run_time):
    pool = multiprocessing.Pool(process_number)
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    
    #add watcher
    watcher = threading.Timer(run_time, force_exit, [pool])
    watcher.start()
    
    for clawer in clawers:
        clawer_tasks = ClawerTask.objects.filter(clawer_id=clawer.id, status=ClawerTask.STATUS_LIVE).order_by("id")[:clawer.settings().dispatch]
        for item in clawer_tasks:
            pool.apply_async(do_run, [item])
        
        print "clawer is %d" % clawer.id
            
    pool.close()
    pool.join()


def force_exit(pool):
    print "force exit after run"
    pool.terminate()
    sys.exit(0)
    

def do_run(clawer_task):
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


class Command(BaseCommand):
    args = ""
    help = "Download clawer task"
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