# coding=utf-8


from optparse import make_option

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.models import Clawer, ClawerTask
from clawer.utils import DownloadQueue, download_clawer_task



def run():
    download_queue = DownloadQueue()
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON).all()
    
    for clawer in clawers:
        clawer_tasks = ClawerTask.objects.filter(clawer_id=clawer.id, status=ClawerTask.STATUS_LIVE).order_by("id")[:clawer.settings().dispatch]
        for item in clawer_tasks:
            download_queue.enqueue(download_clawer_task, [item])
        
        print "clawer is %d, job count %d" % (clawer.id, len(download_queue.jobs))
        
    return download_queue



class Command(BaseCommand):
    args = ""
    help = "Dispatch clawer task"
    option_list = BaseCommand.option_list + (
        make_option('--run',
            dest='run',
            default=290,
            help='Run seconds'
        ),
    )
    
    @wrapper_raven
    def handle(self, *args, **options):
        run()