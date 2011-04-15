# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

import hashlib

from django.db import models
from django.contrib.auth.models import User

def generate_user_id(email):
    m = hashlib.md5()
    m.update(title)
    return m.hexdigest()

class Feed(models.Model):
    name = models.CharField(max_length=100)
    logo = models.URLField()
    url = models.URLField()
    site_uuid = models.CharField(unique=True, max_length=50)
    next_update = models.DateTimeField()
    category = models.CharField(max_length=25)
    addedDate = models.DateTimeField()
    rating = models.CharField(blank=True, max_length=25)
    subscribers = models.IntegerField()
    locked = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s - %s" % (self.name, self.url)

class FeedItem(models.Model):
    site = models.ForeignKey(Feed)
    title = models.CharField(max_length=250)
    story_uuid = models.CharField(unique=True, max_length=50)
    url = models.URLField(max_length=250)
    updatedDate = models.DateTimeField()
    addedDate = models.DateTimeField()
    summary = models.TextField()

    def __unicode__(self):
        return "%s" % (self.title)

class Category(models.Model):
    name = models.CharField(unique=False, max_length=50)

    def __unicode__(self):
        return "%s" % (self.name)

class UserFeed(models.Model):
    feed = models.ForeignKey(Feed)
    name = models.CharField(blank=True, unique=False, max_length=50)
    category = models.ForeignKey(Category)

    def __unicode__(self):
        return "%s - %s" % (self.feed.name, self.category.name)

class UserInbox(models.Model):
    username = models.ForeignKey(User)
    inbox = models.ManyToManyField(FeedItem)

    def __unicode__(self):
        return "%s" % (self.username)

class FeedStaging(models.Model):
    url = models.URLField()
    user = models.CharField(blank=True, max_length=30)
    category = models.CharField(blank=True, max_length=30)

    def __unicode__(self):
        return "%s" % (self.url)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    uuid = models.CharField(max_length=32, blank=True)
    birthdate = models.DateField(blank=True, null=True)
    friends = models.ManyToManyField('self', blank=True)
    feeds = models.ManyToManyField(UserFeed, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    def __unicode__(self):
        return "%s" % (self.user)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

