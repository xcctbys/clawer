#encoding=utf-8


import json
import datetime

from html5helper.decorator import render_json
from clawer.models import Clawer, ClawerTask, ClawerTaskGenerator,\
    ClawerAnalysis, ClawerAnalysisLog, Logger, LoggerCategory, ClawerDownloadLog,\
    RealTimeMonitor
from clawer.utils import check_auth_for_api, EasyUIPager, Download
from clawer.forms import UpdateClawerTaskGenerator, UpdateClawerAnalysis,\
    AddClawerTask, UpdateClawerSetting
from html5helper.utils import get_request_ip



@render_json
@check_auth_for_api
def task_stat(request):
    result = {"is_ok":True, "status":[], "series":[], "xAxis":[]}
    monitor = RealTimeMonitor()
    
    for (status, name) in ClawerTask.STATUS_CHOICES:
        result["status"].append(name)
        
        remote_data = monitor.load_task_stat(status)
        dts = sorted(remote_data["data"].keys())
        if result["xAxis"] == []:
            result["xAxis"] = [x.strftime("%d %H:%M") for x in dts]
        serie = [remote_data["data"][x]["count"] for x in dts]
        result["series"].append(serie)
    
    return result


