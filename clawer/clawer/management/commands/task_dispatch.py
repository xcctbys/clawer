# coding=utf-8


from optparse import make_option

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask, RealTimeMonitor
from clawer.utils import DownloadQueue, download_clawer_task



def run():
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    monitor = RealTimeMonitor()
    
    for clawer in clawers:
        clawer_settting = clawer.cached_settings()
        download_queue = DownloadQueue(clawer_settting.is_urgency())
        clawer_tasks = ClawerTask.objects.filter(clawer_id=clawer.id, status=ClawerTask.STATUS_LIVE).order_by("id")[:clawer_settting.dispatch]
        
        for item in clawer_tasks:
            if not download_queue.enqueue(download_clawer_task, [item]):
                break
            item.status = ClawerTask.STATUS_PROCESS
            item.save()
            #trace it
            monitor.trace_task_status(item)
        
        print "clawer is %d, job count %d" % (clawer.id, len(download_queue.jobs))
        
    return download_queue


def empty_all():
    download_queue = DownloadQueue(False)
    ret = download_queue.queue.empty()
    print ret
    
    urgency_download_queue = DownloadQueue(True)
    urgency_ret = urgency_download_queue.queue.empty()
    print urgency_ret
    
    
class Command(BaseCommand):
    args = ""
    help = "Dispatch clawer task"
    option_list = BaseCommand.option_list + (
        make_option('--empty',
            dest='empty',
            action="store_true",
            help='empty all'
        ),
    )
    
    @wrapper_raven
    def handle(self, *args, **options):
        if options["empty"]:
            empty_all()
            return
        
        run()