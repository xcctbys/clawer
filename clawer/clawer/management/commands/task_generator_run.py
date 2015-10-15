# coding=utf-8

import logging
import subprocess
import traceback
import os
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator, Clawer, ClawerTask,\
    RealTimeMonitor
from clawer.utils import UrlCache, SafeProcess
import json



def run(task_generator_id):
    logging.info("run task generator %d" % task_generator_id)
    
    task_generator = ClawerTaskGenerator.objects.get(id=task_generator_id)
    if not (task_generator.status==ClawerTaskGenerator.STATUS_ON and task_generator.clawer.status==Clawer.STATUS_ON):
        return False
    
    path = task_generator.product_path()
    task_generator.write_code(path)
    
    out_path = "/tmp/task_generator_%d" % task_generator_id
    out_f = open(out_path, "w+b")
    
    monitor = RealTimeMonitor()
    safe_process = SafeProcess([settings.PYTHON, path], stdout=out_f, stderr=subprocess.PIPE)
    
    p = safe_process.run(1800)
    err = p.stderr.read()
    status = safe_process.wait()
    if status != 0:
        logging.error("run task generator %d failed: %s" % (task_generator.id, err))
        out_f.close()
        task_generator.failed_reason = err
        task_generator.last_failed_datetime = datetime.datetime.now()
        task_generator.save()
        return False
    out_f.close()
    
    out_f = open(out_path, "r")
    for line in out_f:
        try:
            js = json.loads(line)
            url_cache = UrlCache(js['uri'])
            if url_cache.has_url():
                raise Exception("%s has exists", js['uri'])
            url_cache.add_it()
            
            clawer_task = ClawerTask.objects.create(clawer=task_generator.clawer, task_generator=task_generator, uri=js["uri"],
                                  cookie=js.get("cookie"))
            #trace it
            monitor.trace_task_status(clawer_task)
        except:
            logging.error("add %s failed: %s", js['uri'], traceback.format_exc(10))
            task_generator.failed_reason = traceback.format_exc(10)
            task_generator.last_failed_datetime = datetime.datetime.now()
            task_generator.save()
    
    out_f.close()
    #os.remove(out_path)
    return True
 
                

class Command(BaseCommand):
    args = "task_generator_id"
    help = "Run task generator"
    
    @wrapper_raven
    def handle(self, *args, **options):
        task_generator_id = int(args[0])
        run(task_generator_id)