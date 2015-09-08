#encoding=utf-8


from html5helper.decorator import render_template


def index(request):
    return render_template("index.html", request=request)


def clawer(request):
    return render_template("clawer/index.html", request=request)


def clawer_all(request):
    return render_template("clawer/all.html", request=request)


def clawer_task(request):
    return render_template("clawer/task.html", request=request)


def clawer_task_failed(request):
    return render_template("clawer/task_failed.html", request=request)