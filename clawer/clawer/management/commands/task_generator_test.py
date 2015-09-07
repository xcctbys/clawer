# coding=utf-8

import datetime
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator, Clawer


def test():
    task_generators = ClawerTaskGenerator.objects.filter(status__in=[ClawerTaskGenerator.STATUS_ALPHA, 
                                                                     ClawerTaskGenerator.STATUS_BETA, 
                                                                     ClawerTaskGenerator.STATUS_PRODUCT])
    
    for task_generator in task_generators:
        if test_alpha(task_generator) is False:
            continue
        if test_beta(task_generator) is False:
            continue
        if test_product(task_generator) is False:
            continue
        #make old offline
        runing = task_generator.clawer.runing_task_generator()
        runing.status = ClawerTaskGenerator.STATUS_OFF
        runing.save()
        
        task_generator.status = ClawerTaskGenerator.STATUS_ON
        task_generator.save()
    
    
def test_alpha(task_generator):
    path = task_generator.alpha_path()
    write_code(task_generator, path)
    pipe = os.popen("%s %s" % (settings.PYTHON, path), "r")
    failed_lines = []
    
    for line in pipe:
        uri = ClawerTaskGenerator.parse_line(line)
        if not uri:
            failed_lines.append(line)
            continue
        print "pipe line: %s " % line
    
    status = pipe.close()    
    if status != None:
        print "abnormal exit, status %s" % (status)
        task_generator.failed_reason = "\n".join(failed_lines)
        task_generator.status = ClawerTaskGenerator.STATUS_TEST_FAIL
        task_generator.save()
        return False 
    
    return True


def test_beta(task_generator):
    return True


def test_product(task_generator):
    return True


def write_code(task_generator, path):
    f = open(path, "w")
    f.write(task_generator.code)
    f.close()
                

class Command(BaseCommand):
    args = ""
    help = ""
    
    @wrapper_raven
    def handle(self, *args, **options):
        test()