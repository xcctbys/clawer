#encoding=utf-8




import json
import traceback
import logging

from html5helper.decorator import render_json
from clawer.models import Clawer
from clawer.utils import check_auth_for_api, EasyUIPager



@render_json
@check_auth_for_api
def clawer_all(request):
    id = request.GET.get("id")
    q = request.POST.get("q")  # use like
    
    queryset = Clawer.objects
    if id:
        queryset = queryset.filter(id=int(id))
    if q:
        queryset = queryset.filter(name__icontains=q)
        
    pager = EasyUIPager(queryset, request)
    return pager.query()