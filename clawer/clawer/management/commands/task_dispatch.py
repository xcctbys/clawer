# coding=utf-8


from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator, Clawer, ClawerTask
from clawer import tasks as celeryTasks


def dispatch():
    clawer_tasks = ClawerTask.objects.filter(status=ClawerTask.STATUS_LIVE).order_by("id")[:500]
    for item in clawer_tasks:
        celeryTasks.run_clawer_task.delay(item)
        
    return True
 


class Command(BaseCommand):
    args = ""
    help = "Dispatch clawer task"
    
    @wrapper_raven
    def handle(self, *args, **options):
        dispatch()