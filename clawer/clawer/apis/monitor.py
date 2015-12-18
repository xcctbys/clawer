#encoding=utf-8

from html5helper.decorator import render_json
from clawer.models import ClawerTask, RealTimeMonitor, ClawerHourMonitor
from clawer.utils import check_auth_for_api, EasyUIPager




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


@render_json
@check_auth_for_api
def hour(request):
    clawer_id = request.GET.get("clawer")
    
    qs = ClawerHourMonitor.objects.all()
    if clawer_id:
        qs = qs.filter(clawer_id=clawer_id)
        
    return EasyUIPager(qs, request).query()



@render_json
@check_auth_for_api
def hour_echarts(request):
    clawer_id = request.GET.get("clawer_id")
    result = {"is_ok":True, "series":[], "xAxis":[]}
    
    qs = ClawerHourMonitor.objects.filter(clawer_id=clawer_id).order_by("hour")
    
    serie = [x.bytes for x in qs]
    result["series"].append(serie)
    
    result["xAxis"] = [x.hour.strftime("%d日%H") for x in qs]
    
    return result