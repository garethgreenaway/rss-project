from mysite.browseFeeds.models import Feed
from mysite.browseFeeds.models import UserFeed
from mysite.browseFeeds.models import UserInbox
from mysite.browseFeeds.models import Category

from django.contrib import admin

class FeedsAdmin(admin.ModelAdmin):
	fields = ['name', 'url', 'next_update'];

admin.site.register(Feed, FeedsAdmin)
admin.site.register(UserFeed)
admin.site.register(UserInbox)
admin.site.register(Category)
