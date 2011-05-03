from django.contrib import admin
from django.conf import settings
from la_facebook.models import UserAssociation

if settings.DEBUG:
    admin.site.register(UserAssociation)
