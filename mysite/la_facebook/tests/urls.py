from django.conf.urls.defaults import *
from django.contrib import admin 
admin.autodiscover()
urlpatterns = patterns('',
    url(r"^la_facebook/", include("la_facebook.urls")),
    (r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',{'next_page':'/'}, name="logout"),
    url(r'^dummy$','la_facebook.tests.views.dummy', name="dummy"),
)

