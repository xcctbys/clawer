#encoding=utf-8
from html5helper.decorator import render_template


def get_all(request):
    return render_template('enterprise/get_all.html', request=request)