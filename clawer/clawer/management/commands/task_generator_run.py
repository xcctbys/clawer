# coding=utf-8

import logging
import os
import subprocess
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator, Clawer, ClawerTask


def run(task_generator_id):
    logging.info("run task generator %d" % task_generator_id)
    
    task_generator = ClawerTaskGenerator.objects.get(id=task_generator_id)
    if not (task_generator.status==ClawerTaskGenerator.STATUS_ON and task_generator.clawer.status==Clawer.STATUS_ON):
        return False
    
    path = task_generator.product_path()
    task_generator.write_code(path)
    
    p = subprocess.Popen([settings.PYTHON, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #("%s %s" % (settings.PYTHON, path), "r")
    for line in p.stdout:
        js = ClawerTaskGenerator.parse_line(line)
        if not js:
            logging.warning("unknown line: %s" % line)
            continue
        #check multiple url
        end = datetime.datetime.now()
        start = end - datetime.timedelta(settings.CLAWER_TASK_URL_MULTIPLE_DAY)
        if ClawerTask.objects.filter(uri=js['uri'], clawer=task_generator.clawer, add_datetime__range=(start, end)).count() > 0:
            logging.info("find multiple url: %s" % line)
            continue
        #insert to db
        ClawerTask.objects.create(clawer=task_generator.clawer, task_generator=task_generator, uri=js["uri"],
                                  cookie=js.get("cookie"))
        
    err = p.stderr.read()
    
    status = p.wait()
    if status != 0:
        logging.error("run task generator %d failed: %s" % (task_generator.id, err))
        return False
    
    return True
 
                

class Command(BaseCommand):
    args = "task_generator_id"
    help = "Run task generator"
    
    @wrapper_raven
    def handle(self, *args, **options):
        task_generator_id = int(args[0])
        run(task_generator_id)