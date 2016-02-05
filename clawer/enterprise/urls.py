#encoding=utf-8

from django.conf.urls import patterns, include, url


api_urls = patterns('enterprise.apis', 
    url(r"^get/all/$", "get_all"),
    url(r"^add/$", "add"),
)

urlpatterns = patterns("enterprise.views", 
    url(r"^get/all/$", "get_all"),
    
    url(r"^api/", include(api_urls)),
)