#encoding=utf-8
# Create your views here.

import random
import traceback

from html5helper.utils import get_request_ip, do_paginator
from html5helper.decorator import render_template, render_json
from captcha.models import Captcha, LabelLog, Category
from django.core.urlresolvers import reverse



def index(request):
    title = u"图片识别"
    category = request.GET.get("category")
    
    random_count = 50
    if category:
        category = int(category)
        captchas = Captcha.objects.filter(label_count__lt=3, category=category)[:random_count]
        captcha_count = Captcha.objects.filter(label_count__gt=2, category=category).count()
        label_count = LabelLog.objects.filter(captcha__category=category).count()
    else:
        captchas = Captcha.objects.filter(label_count__lt=3)[:random_count]
        captcha_count = Captcha.objects.filter(label_count__gt=2).count()
        label_count = LabelLog.objects.count()
        
    if len(captchas) > 1:
        random_index = random.randint(0, len(captchas))
        captcha = captchas[random_index]
    elif len(captchas) == 1:
        captcha = captchas[0]
    else:
        captcha = None
    
    return render_template("captcha/index.html", request=request, captcha_count=captcha_count, label_count=label_count, title=title,
                           captcha=captcha, Category=Category, category_name=Category.name(category))
    
    
def labeled(request, page=1):
    qs = Captcha.objects.filter(label_count__gt=2)
    pager = do_paginator(qs, page, 20)
    prefix = reverse("captcha.views.labeled")
    
    return render_template("captcha/labeled.html", request=request, pager=pager, prefix=prefix)


@render_json
def make_label(request):
    captcha_id = request.POST.get("captcha_id")
    label = request.POST.get("label")
    
    try:
        captcha = Captcha.objects.get(id=captcha_id)
    except:
        return {"is_ok":False, "reason": traceback.format_exc(1)}
    
    if not label.strip():
        return {"is_ok":False, "reason":u"文字不能为空"}
    
    captcha.label_count += 1
    captcha.save()
    
    LabelLog.objects.create(captcha=captcha, label=label, ip=get_request_ip(request))
    return {"is_ok":True}


@render_json
def all_labeled(request):
    category = int(request.GET.get("category"))
    qs = Captcha.objects.filter(label_count__gt=2, category=category)
    
    return {"is_ok":True, "captchas":[x.as_json() for x in qs]}