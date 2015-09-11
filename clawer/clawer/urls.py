from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin



admin.autodiscover()


#apis 
user_api_urls = patterns("clawer.apis.user", 
    url(r"^login/$", "login"),
    url(r"^logout/$", "logout"),
    url(r"^keepalive/$", "keepalive"),
    url(r"^is/logined/$", "is_logined"),
    
    url(r"^my/menus/$", "get_my_menus"),

)

home_api_urls = patterns("clawer.apis.home",
    url(r"^clawer/all/$", "clawer_all"),
    
    url(r"^clawer/task/$", "clawer_task"),
    url(r"^clawer/task/failed/$", "clawer_task_failed"),
    url(r"^clawer/task/generator/update/$", "clawer_task_generator_update"),
    url(r"^clawer/task/generator/history/$", "clawer_task_generator_history"),
    
    url(r"^clawer/analysis/history/$", "clawer_analysis_history"),
    url(r"^clawer/analysis/log/$", "clawer_analysis_log"),
    url(r"^clawer/analysis/update/$", "clawer_analysis_update"),
)

apis_urls = patterns("clawer.apis", 
    url(r"^user/", include(user_api_urls)),
    url(r"^home/", include(home_api_urls)),
)

#views
urlpatterns = patterns('clawer.views.home',
    # Examples:
    url(r'^$', 'index'),
    
    url(r'^clawer/$', "clawer"),
    url(r'^clawer/all/$', "clawer_all"),
    url(r"^clawer/task/failed/$", "clawer_task_failed"),
    url(r"^clawer/task/$", "clawer_task"),
    url(r"^clawer/analysis/log/$", "clawer_analysis_log"),
    
    
    url(r'^apis/', include(apis_urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
