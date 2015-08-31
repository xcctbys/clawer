#coding=utf-8
from __future__ import absolute_import

from celery import shared_task

@shared_task
def write_db(model_object, **kwargs):
    model_object.do_save(**kwargs)
    return model_object.id