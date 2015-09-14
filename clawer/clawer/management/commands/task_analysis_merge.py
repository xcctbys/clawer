# coding=utf-8
""" run every hour
"""

import json
import traceback
import threadpool
import os
import subprocess
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerAnalysisLog



def run():
    pre_hour = datetime.datetime.now() - datetime.timedelta(minutes=60)
    start = pre_hour.replace(minute=0, second=0)
    end = pre_hour.replace(minute=59, second=59)
    
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON)
    for item in clawers:
        merge_clawer(item, start, end)
        
    return True


def merge_clawer(clawer, start, end):
    analysis_logs = ClawerAnalysisLog.objects.filter(clawer=clawer, add_datetime__range=(start, end), status=ClawerAnalysisLog.STATUS_SUCCESS)
    
    with open(save_path(clawer, start), "w") as f:
        for item in analysis_logs:
            f.write(item.result)
        

def save_path(clawer, dt):
    path = os.path.join(settings.CLAWER_RESULT, "%d/%s/%s.json" % (clawer.id, dt.strftime("%Y/%m/%d"), dt.strftime("%H")))
    parent = os.path.dirname(path)
    if os.path.exists(parent) is False:
        os.makedirs(parent, 0775)
    return path
        

class Command(BaseCommand):
    args = ""
    help = "Merge Analysis Result. Always merge previous hour"
    
    @wrapper_raven
    def handle(self, *args, **options):
        run()