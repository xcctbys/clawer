# coding=utf-8

from crontab import CronTab

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator



def test():
    task_generators = ClawerTaskGenerator.objects.filter(status__in=[ClawerTaskGenerator.STATUS_ALPHA, 
                                                                     ClawerTaskGenerator.STATUS_BETA, 
                                                                     ClawerTaskGenerator.STATUS_PRODUCT]).order_by("id")
    
    for task_generator in task_generators:
        print "test %d" % task_generator.id
        
        if test_alpha(task_generator) is False:
            continue
        if test_beta(task_generator) is False:
            continue
        if test_product(task_generator) is False:
            continue
        
        task_generator.status = ClawerTaskGenerator.STATUS_ON
        task_generator.save()
        
        print "success %d" % task_generator.id
        #make old offline
        ClawerTaskGenerator.objects.filter(clawer_id=task_generator, \
            status=ClawerTaskGenerator.STATUS_ON).exclude(id=task_generator.id).update(status=ClawerTaskGenerator.STATUS_OFF)
    
    
def test_alpha(task_generator):
    path = task_generator.alpha_path()
    task_generator.write_code(path)
    print "alpha test success"
    return True


def test_beta(task_generator):
    user_cron = CronTab(user=settings.CRONTAB_USER)
    job = user_cron.new(command="/usr/bin/echo")
    job.setall(task_generator.cron.strip())
    if job.is_valid() == False:
        task_generator.failed_reason = u"crontab 格式出错"
        task_generator.status = ClawerTaskGenerator.STATUS_TEST_FAIL
        task_generator.save()
        print task_generator.failed_reason
        return False
    
    task_generator.status = ClawerTaskGenerator.STATUS_BETA
    task_generator.save()
    print "beta test success"
    return True


def test_product(task_generator):
    
    comment = "clawer %d task generator" % task_generator.clawer_id
    user_cron = CronTab(user=settings.CRONTAB_USER)
    user_cron.remove_all(comment=comment)
    user_cron.write_to_user(user=settings.CRONTAB_USER)
    
    job = user_cron.new(command="cd /home/webapps/nice-clawer/confs/production; ./bg_cmd.sh task_generator_run %d" % (task_generator.id), comment=comment)
    job.setall(task_generator.cron.strip())
    if job.is_valid() == False:
        task_generator.failed_reason = u"crontab 安装出错"
        task_generator.status = ClawerTaskGenerator.STATUS_TEST_FAIL
        task_generator.save()
        print task_generator.failed_reason
        return False
    user_cron.write_to_user(user=settings.CRONTAB_USER)
    
    task_generator.status = ClawerTaskGenerator.STATUS_PRODUCT
    task_generator.save()
    return True

                

class Command(BaseCommand):
    args = ""
    help = ""
    
    @wrapper_raven
    def handle(self, *args, **options):
        test()