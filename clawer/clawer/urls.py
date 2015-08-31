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
    
    url(r'^apis/', include(apis_urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
