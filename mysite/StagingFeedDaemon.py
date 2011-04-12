#!/usr/bin/env python

import feedparser
import hashlib
import psycopg2
import sys
import re
import random
import time

from celery.task import task
from RepeatTimer import RepeatTimer
from threading import Thread, Timer
from Queue import Queue

#
# Pull in the django support
#
from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import connection
from django.contrib.auth.models import User
from browseFeeds.models import FeedStaging, Feed, UserFeed, Tag

def worker(input, output):
	for item in iter(input.get, 'STOP'):
		result = addFeed(item)

def generate_uuid(title):
	m = hashlib.md5()
	m.update(title)
	return m.hexdigest()

@task
def addFeed(item):

	url = item.url

	if len(item.user) > 0:
		user = User.objects.get(username=item.user)

		if len(item.tag) > 0:
			if Tag.objects.filter(user=user, tag_name=item.tag):
				tag = Tag.objects.get(user=user, tag_name = item.tag)
			else:
				tag = Tag.objects.create(user=user, tag_name=item.tag)
		else:
			tag = None
	else:
		user = None
		tag = None

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
		nextUpdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now + jitter))
		addedDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))

		f = Feed(name=siteName, url=url, logo=site_logo, site_uuid=site_uuid, next_update = nextUpdate, addedDate=addedDate, subscribers = 0, locked = False)
		f.save()

		if user:
			subscribedFeeds_query = UserFeed.objects.filter(username=user, feed=f)

			if not subscribedFeeds_query:
				if tag:
					print "Subscribing %s to %s with tag %s" % (user.username, siteName, tag.tag_name)
					uf = UserFeed.objects.create(username=user, feed=f)
					uf.tags.add(tag)
				else:	
					print "Subscribing %s to %s" % (user.username, siteName)
					uf = UserFeed.objects.create(username=user, feed=f)
                
                f.subscribers += 1
                f.save()

	else:
		if user:
			f = Feed.objects.filter(url__exact=url)[0]
			siteName = f.name

			subscribedFeeds_query = UserFeed.objects.filter(username=user, feed=f)

			if not subscribedFeeds_query:
				if tag:
					print "Subscribing %s to %s with tag %s" % (user.username, siteName, tag.tag_name)
					uf = UserFeed.objects.create(username=user, feed=f)
					uf.tags.add(tag)
				else:	
					print "Subscribing %s to %s" % (user.username, siteName)
					uf = UserFeed.objects.create(username=user, feed=f)

                f.subscribers += 1
                f.save()

	connection.close()
	return


def run():

	print "Checking for updates at " + time.asctime()

	NUMBER_OF_PROCESSES = 4

	#
	# Create queues
	#
	task_queue = Queue()
	done_queue = Queue()

	# 
	# Pull feeds out to gather items from
	#
	AllFeeds = FeedStaging.objects.all()
	UniqueFeeds = AllFeeds
	#UniqueFeeds = FeedStaging.objects.values('url')

	#
	# If nothing is scheduled, just return.
	#
	if len(UniqueFeeds) == 0:
		return

	#
	# Add the urls to the queue to be processed
	#
	for item in AllFeeds:
		task_queue.put(item)

	#
	# Start up our workers to process the queue
	#
	for i in range(NUMBER_OF_PROCESSES):
		Thread(target=worker, args=(task_queue, done_queue)).start()
	
	#
	# We're done, so tell all the workers to stop
	#
	for i in range(NUMBER_OF_PROCESSES):
		task_queue.put('STOP')

	#
	for i in AllFeeds:
		print "Deleting %s from the staging queue." % (i.url)
		i.delete()

if __name__ == '__main__':

	try:
		run()
		r = RepeatTimer(10.0, run)
		r.start()
	except (EOFError, KeyboardInterrupt):
		sys.exit()
	

