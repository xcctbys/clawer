# coding=utf-8

import logging
import os
import subprocess

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
        uri = ClawerTaskGenerator.parse_line(line)
        if not uri:
            logging.warning("unknown line: %s" % line)
            continue
        #insert to db
        task = ClawerTask.objects.create(clawer=task_generator.clawer, task_generator=task_generator, uri=uri)
        
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