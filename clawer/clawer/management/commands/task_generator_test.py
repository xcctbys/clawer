# coding=utf-8

import os
import subprocess
import sys
from crontab import CronTab

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
    p = subprocess.Popen([settings.PYTHON, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #("%s %s" % (settings.PYTHON, path), "r")
    for line in p.stdout:
        uri = ClawerTaskGenerator.parse_line(line)
        if not uri:
            continue
        print "stdout: %s " % line
        
    err = p.stderr.read()
    status = p.wait()
    if status != 0:
        print "abnormal exit, status %s" % (status)
        task_generator.failed_reason = err
        task_generator.status = ClawerTaskGenerator.STATUS_TEST_FAIL
        task_generator.save()
        return False 
    
    return True


def test_beta(task_generator):
    user_cron = CronTab(user=settings.CRONTAB_USER)
    job = user_cron.new(command="/usr/bin/echo")
    job.setall(task_generator.cron)
    if job.is_valid() == False:
        task_generator.failed_reason = u"crontab 格式出错"
        task_generator.status = ClawerTaskGenerator.STATUS_TEST_FAIL
        task_generator.save()
        return
    task_generator.status = ClawerTaskGenerator.STATUS_BETA
    task_generator.save()
    return True


def test_product(task_generator):
    task_generator.status = ClawerTaskGenerator.STATUS_ON
    task_generator.save()
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