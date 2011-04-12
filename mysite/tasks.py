import feedparser
import hashlib
import psycopg2
import sys
import re
import random
import time
import dateutil.parser

from celery.task import task
from celery.execute import send_task

from RepeatTimer import RepeatTimer
from threading import Thread, Timer
from Queue import Queue

#
# Pull in the django support
#
from django.core.management import setup_environ
import settings
setup_environ(settings)

from browseFeeds.models import Feed, FeedItem, UserFeed, Category
from datetime import tzinfo, timedelta, datetime

from django.db import connection
from django.contrib.auth.models import User

@task
def add(x, y):
	return x + y

@task(ignore_result=True)
def hello():

	logger = hello.get_logger()

	for item in Feed.objects.filter(next_update__lte=datetime.now(), locked__exact=False):
		#
		# Lock the Feed until its been updated
		#
		item.locked = True
		item.save()

		logger.info("Updating stories for %s" % (item.url))
		grabStories.apply_async(args=[item.url], queue="stories", routing_key="stories")

def generate_uuid(title):
    m = hashlib.md5()
    m.update(title)
    return m.hexdigest()

@task(ignore_result=True)
def task_addCategory(user, category):

    user = User.objects.get(username=user)

    if Category.objects.filter(user=user, name=category):
        # Category already exists, ignore the request
        pass
    else:
        category = Category.objects.create(user=user, name=category)
        category.save()

    return

@task(ignore_result=True)
def task_addFeed(item):

    print "Item is: ",
    print item

    url = item.url
    user = User.objects.get(username=item.user)

    #if len(item.user) > 0:
    #    user = User.objects.get(username=item.user)
    #
    #    if len(item.category) > 0:
    #        if Tag.objects.filter(user=user, tag_name=item.tag):
    #            tag = Tag.objects.get(user=user, tag_name = item.tag)
    #        else:
    #            tag = Tag.objects.create(user=user, tag_name=item.tag)
    #    else:
    #        tag = None
    #else:
    #    user = None
    #    tag = None

    category = Category.objects.get(user=user, name=item.category)

    if not Feed.objects.filter(url__exact=url):
	
        d = feedparser.parse(url)
        siteName = d.feed.title
        print "Adding: %s" % (siteName)

	    #
        # UUID for the website we're pulling the feed from
        #
        site_uuid = generate_uuid(url)

        #
        # Site Logo
        #
        if d.feed.get("image"):
            site_logo = d.feed.image.href
        else:
            site_logo = "http://theme.wiked.org/images/empty.png"
	
        now = time.time()
        jitter = random.randint(1,2) * 60
        nextUpdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        addedDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
		
        f = Feed(name=siteName, url=url, logo=site_logo, site_uuid=site_uuid, next_update = nextUpdate, addedDate=addedDate, subscribers = 0, locked = False)
        f.save()

        # Added the new feed to the queue to be updated
        grabStories.apply_async(args=[url], queue="stories", routing_key="stories")

        #
        # Put the new feed on the queue to update
        #

        if user:
            subscribedFeeds_query = UserFeed.objects.filter(username=user, feed=f)

            if not subscribedFeeds_query:
                print "Subscribing %s to %s with category %s" % (user.username, siteName, category.name)
                uf = UserFeed.objects.create(username=user, feed=f, category=category)

                f.subscribers += 1
                f.save()

    else:
        if user:
            f = Feed.objects.filter(url__exact=url)[0]
            siteName = f.name

            subscribedFeeds_query = UserFeed.objects.filter(username=user, feed=f)

            if not subscribedFeeds_query:
                    print "Subscribing %s to %s with tag %s" % (user.username, siteName, category.name)
                    uf = UserFeed.objects.create(username=user, feed=f, category=category)

    connection.close()
    return

@task(ignore_result=True)
def grabStories(url):

	logger = grabStories.get_logger()

	d = feedparser.parse(url)

	#
	# UUID for the website we're pulling the feed from
	#
	site_uuid = generate_uuid(url)

	site = Feed.objects.filter(site_uuid__exact=site_uuid)[0]

	stories = []

	logger.info("%d entries found." % (e.title))

	for i in range(0, len(d.entries)):

		e = d.entries[i]

		#
		# UUID for the Url to the story
		#
		story_uuid = generate_uuid(e.link)
		story_title = e.title

		if getattr(e, 'summary', False):
			summary = e.summary
		elif getattr(e, 'subtitle', False):
			summary = e.subtitle
		else:
			pass

		now = time.time()

		if hasattr(e, "updated"):
			#
			# Noticed a few feed items with invalid dates.
			#
			e.updated = re.sub(" 24:", " 00:", e.updated)
	
			addedDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
			updatedDate = dateutil.parser.parse(e.updated, ignoretz=True).strftime("%Y-%m-%d %H:%M:%S")

		else:
			addedDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
			updatedDate = addedDate

		if not FeedItem.objects.filter(story_uuid__exact=story_uuid):

			logger.info("Adding %s" % (e.title))

			try:
				f = FeedItem(site=site, title=story_title, story_uuid=story_uuid, url=e.link, updatedDate=updatedDate, addedDate=addedDate, summary=summary)
				f.save()
			except:
				logger.info("Something went wrong, Skipping %s" % (e.title))


		else:		

			logger.info("%s already exists." % (e.title))
	
	#
	# Schedule the next feed update
	#
	now = time.time()
	jitter = random.randint(15,20) * 60
	nextUpdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now + jitter))
	site.next_update = nextUpdate
	site.locked = False
	site.save()
	logger.info("Updating next refresh to %s" % (nextUpdate))
	
	#
	# Close the connection to the database
	#
	connection.close()
	return


