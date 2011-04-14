import time
from datetime import timedelta, datetime, tzinfo

#
# Pull in the django support
#
from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import connection
from browseFeeds.models import FeedItem, UserFeed, UserInbox, FeedStaging, Feed, Category, UserProfile
from django.contrib.auth.models import User

class GMT(tzinfo):
	def __init__(self):

		dt = datetime.utcnow()

		d = datetime(dt.year, 4, 1)
		self.dston = d - timedelta(days=d.weekday() + 1)
		d = datetime(dt.year, 11, 1)
		self.dstoff = d - timedelta(days=d.weekday() + 1)

	def utcoffset(self, dt):
		return timedelta(hours=1) + self.dst(dt)

	def dst(self, dt):
		if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
			return timedelta(hours=2)
		else:
			return timedelta(hours=0)

	def tzname(self,dt):
		return "GMT"


def inspect_feeds():
    for item in Feed.objects.all():
        print item.name
        print item.next_update
        print item.addedDate
        print item.site_uuid
        print item.locked
        print ""

def inspect_feed_items(uuid):

    if not uuid:
        print "Usage: inspect_feed_items site-uuid"

    else:
        for item in FeedItem.objects.filter(site__site_uuid__exact=uuid):
            print item.title
            print item.updatedDate
            print item.addedDate
            print ""

def queue_feeds():
    for item in Feed.objects.all():
        item.next_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 300))
        item.locked = False
        item.save()
