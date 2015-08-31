from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin



admin.autodiscover()

user_api_urls = patterns("clawer.apis.user", 
    url(r"^login/$", "login"),
    url(r"^logout/$", "logout"),
    url(r"^keepalive/$", "keepalive"),
    url(r"^is/logined/$", "is_logined"),
    
    url(r"^my/menus/$", "get_my_menus"),

)

api_urls = patterns("clawer.apis", 
    url(r"^user/", include(user_api_urls)),
)

clawer_urls = patterns("clawer.views", 
    url(r"^$", "clawer"),
    
    url(r"^api/", include(api_urls)),
)

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'clawer.views.index'),
    url(r'^clawer/', include(clawer_urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
