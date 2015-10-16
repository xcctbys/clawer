from django.conf.urls import patterns, include, url



urlpatterns = patterns('captcha.views',
    # Examples:
    url(r'^$', 'index'),
    url(r"^make/label/$", "make_label"),
)
