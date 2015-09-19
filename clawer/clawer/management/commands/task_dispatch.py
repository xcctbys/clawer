# coding=utf-8


from django.core.management.base import BaseCommand
from django.core.cache import cache

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator, Clawer, ClawerTask
from clawer import tasks as celeryTasks


LAST_DISPATCH_ID_KEY = "task_dispatch_last_id"


def dispatch():
    last_id = cache.get(LAST_DISPATCH_ID_KEY, 0)
    clawer_tasks = ClawerTask.objects.filter(status=ClawerTask.STATUS_LIVE, clawer__status=Clawer.STATUS_ON, id__gt=last_id).order_by("id")[:500]
    
    for item in clawer_tasks:
        celeryTasks.run_clawer_task.delay(item)
        last_id = item.id
        
    cache.set(LAST_DISPATCH_ID_KEY, last_id, 3600*24)
    print "last id is %d" % last_id
    return True



class Command(BaseCommand):
    args = ""
    help = "Dispatch clawer task"
    
    @wrapper_raven
    def handle(self, *args, **options):
        dispatch()