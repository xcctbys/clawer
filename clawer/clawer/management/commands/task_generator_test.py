# coding=utf-8

import datetime

from django.core.management.base import BaseCommand

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
    return True


def test_beta(task_generator):
    return True


def test_product(task_generator):
    return True
                

class Command(BaseCommand):
    args = ""
    help = ""
    
    @wrapper_raven
    def handle(self, *args, **options):
        test()