#encoding=utf-8




import json
import traceback
import logging

from html5helper.decorator import render_json
from clawer.models import Clawer, ClawerTask, ClawerTaskGenerator
from clawer.utils import check_auth_for_api, EasyUIPager
from clawer.forms import UpdateClawerTaskGenerator



@render_json
@check_auth_for_api
def clawer_all(request):
    obj_id = request.GET.get("obj_id")
    q = request.POST.get("q")  # use like
    
    queryset = Clawer.objects
    if obj_id:
        queryset = queryset.filter(id=int(obj_id))
    if q:
        queryset = queryset.filter(name__icontains=q)
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_task_failed(request):
    queryset = ClawerTask.objects.filter(status=ClawerTask.STATUS_FAIL)
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_task(request):
    status = request.GET.get("status")
    
    queryset = ClawerTask.objects
    if status:
        queryset = queryset.filter(status=status) 
        
    pager = EasyUIPager(queryset, request)
    return pager.query()


@render_json
@check_auth_for_api
def clawer_task_generator_update(request):
    form = UpdateClawerTaskGenerator(request.POST, request.FILES)
    if form.is_valid() is False:
        return {"is_ok":False, "reason": u"%s" % form.errors}
    
    code_file = request.FILES["code_file"]
    if code_file.name[-3:] != ".py":
        return {"is_ok":False, "reason":u"暂时只支持python文件"}
    
    code = code_file.read()
    
    task_generator = ClawerTaskGenerator.objects.create(clawer=form.cleaned_data["clawer"],
                                                        cron=form.cleaned_data["cron"],
                                                        code=code)
    
    return {"is_ok":True, "task_generator":task_generator.as_json()}
    
    
@render_json
@check_auth_for_api
def clawer_task_generator_history(request):
    clawer_id = request.GET.get("clawer_id")
    
    qs = ClawerTaskGenerator.objects.filter(clawer_id=clawer_id)
    pager = EasyUIPager(qs, request)
    return pager.query()