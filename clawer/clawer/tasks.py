#coding=utf-8

from __future__ import absolute_import

from celery import shared_task


@shared_task
def run_clawer_task(clawer_task):
    
    return clawer_task.id


