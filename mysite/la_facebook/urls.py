from django.conf.urls.defaults import *


urlpatterns = patterns("la_facebook.views",
    url(
        regex = r"^login/?$",
        view = "facebook_login",
        name = "la_facebook_login",
    ),
    url(
        regex = r"^callback/?$",
        view = "facebook_callback",
        name = "la_facebook_callback"
    ),
)
