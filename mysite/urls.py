from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.conf import settings

from django.http import HttpResponse

from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#    (r'^account/login/$', 'mysite.browseFeeds.views.site_login'),
#    (r'^account/logout/$', 'mysite.browseFeeds.views.site_logout'),
#    (r'^account/register/$', 'mysite.browseFeeds.views.site_register'),
#    (r'^account/profile/$', 'mysite.browseFeeds.views.index'),

urlpatterns = patterns('',
    (r'^$', 'mysite.browseFeeds.views.index'),
    (r'^search/$', 'mysite.browseFeeds.views.search'),
    (r'^inbox/$', 'mysite.browseFeeds.views.viewInbox'),
    (r'^admin/', include(admin.site.urls)),
    (r'^story/share/(?P<story_uuid>\w+)/$', 'mysite.browseFeeds.views.shareStory_view'),
    (r'^story/shared/$', 'mysite.browseFeeds.views.storyShared'),
    (r'^feed/add/$', 'mysite.browseFeeds.views.addFeed_view'),
    (r'^feed/edit/(?P<feed_uuid>\w+)/$', 'mysite.browseFeeds.views.editFeed_view'),
    (r'^feed/share/$', 'mysite.browseFeeds.views.shareFeed_view'),
    (r'^feed/subscribe/(?P<feed_uuid>\w+)/$', 'mysite.browseFeeds.views.subscribeFeed_view'),
    (r'^feed/thanks/$', 'mysite.browseFeeds.views.feedThanks'),
    (r'^feed/site/(?P<feed_uuid>\w+)/$', 'mysite.browseFeeds.views.index'),
    (r'^feed/site/(?P<feed_uuid>\w+)/(?P<story_uuid>\w+)/$', 'mysite.browseFeeds.views.index'),
    (r'^category/add/$', 'mysite.browseFeeds.views.addCategory_view'),
    (r'^category/submitted/$', 'mysite.browseFeeds.views.categorySubmitted'),
    (r'^facebook_debug/', direct_to_template, {'template':'facebook_debug.html'}),  
    (r'^accounts/', include('registration.urls')),
    url(r"^la_facebook/login/", include("la_facebook.urls"), {'display': 'popup'}),
    url(r"^la_facebook/callback/", include("la_facebook.urls")),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^icons/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './templates/www/icons'}),
        (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './templates/www/images'}),
        (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './templates/www/js'}),
        (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './templates/www/css'}),
        (r'^test/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './templates/www/test'}),
        (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain"))
    )

