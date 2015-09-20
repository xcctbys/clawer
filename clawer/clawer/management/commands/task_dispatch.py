# coding=utf-8
import datetime

from django.core.management.base import BaseCommand
from django.core.cache import cache

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask
from clawer import tasks as celeryTasks


LAST_DISPATCH_ID_KEY = "task_dispatch_last_id"


def dispatch():
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    for clawer in clawers:
        key = "%s_%d" % (LAST_DISPATCH_ID_KEY, clawer.id)
        last_id = cache.get(key, 0)
        dispatch_count = clawer.settings().dispatch
        clawer_tasks = ClawerTask.objects.filter(status=ClawerTask.STATUS_LIVE, clawer=clawer, id__gt=last_id).order_by("id")[:dispatch_count]
        
        for item in clawer_tasks:
            celeryTasks.run_clawer_task.delay(item)
            last_id = item.id
            
        cache.set(LAST_DISPATCH_ID_KEY, last_id, 3600*4)
        print "clawer %d last id is %d" % (clawer.id, last_id)
        
        reset_failed(clawer)
        reset_process(clawer)
        
    return True


def reset_failed(clawer):
    last_done = datetime.datetime.now() - datetime.timedelta(1)
    ClawerTask.objects.filter(status=ClawerTask.STATUS_FAIL, done_datetime__lt=last_done, clawer=clawer).update(status=ClawerTask.STATUS_LIVE)


def reset_process(clawer):
    last_done = datetime.datetime.now() - datetime.timedelta(7)
    ClawerTask.objects.filter(status=ClawerTask.STATUS_PROCESS, done_datetime__lt=last_done, clawer=clawer).update(status=ClawerTask.STATUS_LIVE)




class Command(BaseCommand):
    args = ""
    help = "Dispatch clawer task"
    
    @wrapper_raven
    def handle(self, *args, **options):
        dispatch()