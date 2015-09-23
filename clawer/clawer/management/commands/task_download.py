# coding=utf-8

import multiprocessing
from optparse import make_option
import sys
import threading

from django.core.management.base import BaseCommand

from html5helper.utils import wrapper_raven
from clawer.utils import DownloadWorker



def run(process_number, run_time):
    pool = multiprocessing.Pool(process_number)
    
    #add watcher
    watcher = threading.Timer(run_time, force_exit, [pool])
    watcher.start()
    
    pool.apply_async(do_run)
            
    pool.close()
    pool.join()


def force_exit(pool):
    print "force exit after run"
    pool.terminate()
    sys.exit(0)
    

def do_run():
    worker = DownloadWorker()
    worker.run()


class Command(BaseCommand):
    args = ""
    help = "Download clawer task"
    option_list = BaseCommand.option_list + (
        make_option('--process',
            dest='process',
            default=4,
            help='Pool process number.'
        ),
        make_option('--run',
            dest='run',
            default=290,
            help='Run seconds'
        ),
    )
    
    @wrapper_raven
    def handle(self, *args, **options):
        process_number = int(options["process"])
        run_time = int(options["run"])
        run(process_number, run_time)