# coding=utf-8

from crontab import CronTab

from django.core.management.base import BaseCommand
from django.conf import settings

from html5helper.utils import wrapper_raven
from clawer.models import ClawerTaskGenerator, ClawerSetting, Clawer

import random
from optparse import make_option


def install(foreign=False):
    remove_unused(foreign)
    
    clawers = Clawer.objects.filter(status=Clawer.STATUS_ON)
    for clawer in clawers:
        clawer_setting = clawer.settings()
        print "foreign %s, prior %d" % (foreign, clawer_setting.prior)
        if foreign and clawer_setting.prior != ClawerSetting.PRIOR_FOREIGN:
            continue
        if foreign is False and clawer_setting.prior == ClawerSetting.PRIOR_FOREIGN:
            continue
        
        try:
            task_generator = ClawerTaskGenerator.objects.filter(clawer=clawer).latest()
        except:
            continue
            
        if test_alpha(task_generator) is False:
            continue
        if test_beta(task_generator) is False:
            continue
        if test_product(task_generator, foreign) is False:
            continue
        
        task_generator.status = ClawerTaskGenerator.STATUS_ON
        task_generator.save()
        
        print "success %d" % task_generator.id
        #make old offline
        ClawerTaskGenerator.objects.filter(clawer_id=task_generator, \
            status=ClawerTaskGenerator.STATUS_ON).exclude(id=task_generator.id).update(status=ClawerTaskGenerator.STATUS_OFF)
    
    
def remove_unused(foreign=False):
    clawers = Clawer.objects.filter(status=Clawer.STATUS_OFF)
    
    for clawer in clawers:
        test_crontab(clawer.runing_task_generator(), foreign)

    
def test_alpha(task_generator):
    path = task_generator.alpha_path()
    task_generator.write_code(path)
    return True


def test_beta(task_generator):
    user_cron = CronTab(user=settings.CRONTAB_USER)
    job = user_cron.new(command="/usr/bin/echo")
    job.setall(task_generator.cron.strip())
    if job.is_valid() == False:
        task_generator.cron = "%d * * * *" % random.randint(1, 59)
    
    return True



def test_product(task_generator, foreign):
    test_crontab(task_generator, foreign)
    return True


def test_crontab(task_generator, foreign):
    comment = "clawer %d task generator" % task_generator.clawer_id
    user_cron = CronTab(user=settings.CRONTAB_USER)
    user_cron.remove_all(comment=comment)
    user_cron.write_to_user(user=settings.CRONTAB_USER)
    
    if task_generator.status == ClawerTaskGenerator.STATUS_OFF:
        return
    
    prior = task_generator.clawer.settings().prior
    if foreign and prior != ClawerSetting.PRIOR_FOREIGN:
        return
    
    cmd = "./bg_cmd.sh"
    if prior == ClawerSetting.PRIOR_FOREIGN:
        cmd = "./foreign_bg_cmd.sh"
    
    job = user_cron.new(command="cd /home/webapps/nice-clawer/confs/production; %s task_generator_run %d" % (cmd, task_generator.id), comment=comment)
    job.setall(task_generator.cron.strip())
    
    user_cron.write_to_user(user=settings.CRONTAB_USER)
    
                

class Command(BaseCommand):
    args = ""
    help = "Install generator"
    option_list = BaseCommand.option_list + (
        make_option('--foreign',
            dest='foreign',
            action="store_true",
            default=False,
            help='Run task generators of foreigh'
        ),
    )
    
    
    @wrapper_raven
    def handle(self, *args, **options):
        install(options["foreign"])
