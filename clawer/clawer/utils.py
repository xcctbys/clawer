#coding=utf-8
import math

from html5helper.utils import do_paginator



def check_auth_for_api(view_func):
    """ mobile GET must have secret="", return dict
    """
    def wrap(request, *args, **kwargs):
        if request.user and request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        
        login_error = {"is_ok":False, "reason":u"登陆凭证已经失效，请重新登陆", "login_timeout":True}
        return login_error
    return wrap
    

class EasyUIPager(object):
    
    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request
        
    def query(self):
        """ return dict
        """
        page = int(self.request.GET.get("page", '1'))
        rows = int(self.request.GET.get("rows", '20'))
        sort = self.request.GET.get("sort", "id")
        order = self.request.GET.get("order", "desc")
        
        result = {"is_ok":True, "rows":[], "total":0, "page": page, "total_page":0}
        
        def get_order(o):
            return "" if o == "asc" else "-"
        
        qs = self.queryset
        if sort:
            items = qs.order_by("%s%s" % (get_order(order), sort))
        else:
            items = qs
        pager = do_paginator(items, page, rows)
        result["total"] = pager.paginator.count
        result["rows"] = [x.as_json() for x in pager]
        result["total_page"] = math.ceil(float(result["total"])/rows)
        
        return result
        
        