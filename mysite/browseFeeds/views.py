import re

from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.forms.formsets import formset_factory

from django.contrib.auth.models import User

from mysite.browseFeeds.models import FeedItem, UserFeed, UserInbox, FeedStaging, Feed, Category, UserProfile
from mysite.browseFeeds.forms import AddFeedForm, AddCategoryForm, SubscribeFeedForm, ShareStoryForm, EditFeedForm
from mysite.tasks import task_addFeed, task_addCategory, task_subscribeFeed

from datetime import datetime

import facebook.djangofb as facebook

import logging
import random

logger = logging.getLogger(__name__)

def json_response(data):
	from django.utils import simplejson
	json = simplejson.dumps(data, ensure_ascii=False, default=encode_myway)
	return HttpResponse(json, mimetype='application/json', content_type='application/json; charset=UTF-8')

def encode_myway(obj):

	if isinstance(obj, FeedItem):
		return [obj.title,
			obj.url]
	else:
		raise TypeError(repr(obj) + " is not JSON serializable!")

def index(request, feed_uuid = None, story_uuid = None):

    c = {}
    c.update(csrf(request))
    
    latest_news = []
    mycategories = []

    feeds = []
    mcategories = []

    if request.user.username:

        user = User.objects.filter(username__exact=request.user.username)[0]
        profile = user.profile
        mcategories = profile.categories.order_by('name')
        feeds = profile.feeds.all()

    myFeeds = []
    for feed in feeds:
        myFeeds.append(feed.feed) 
        
    if feed_uuid:
        site = Feed.objects.filter(site_uuid=feed_uuid)[0]
        feeditems = FeedItem.objects.filter(site=site).order_by('-updatedDate').annotate()[:10]	

        if site in myFeeds:
            site_subscribed = True
        else:
            site_subscribed = False

    if story_uuid:
        story = FeedItem.objects.filter(story_uuid=story_uuid)[0]

    recent_feeds = Feed.objects.all().order_by("-addedDate")
    popular_feeds = Feed.objects.all().order_by("-subscribers")[:8]

    for category in mcategories:
        mycategories.append({"category": category, "feeds": feeds.filter(category=category).order_by("feed__name")})

    #
    # return the last 10 feed items
    #
    FeedItems = FeedItem.objects.filter(site__in=myFeeds).order_by('-addedDate')[:10]

    for feedItem in FeedItems:
        summary = re.sub(r'<[^>]*?>', '', feedItem.summary)
        if feedItem.site.logo:
            site_logo = feedItem.site.logo
        else:
            #site_logo = "http://theme.wiked.org/images/empty.png"
            site_logo = ""

        if len(summary) > 300:
            summary = summary[:300] + "[...]"
        else:
            summary = summary

        latest_news.append({"uuid": feedItem.story_uuid, "title": feedItem.title, "summary": summary, "url": feedItem.url, "logo": site_logo})

    return render_to_response('news/index.html', locals(), context_instance=RequestContext(request))

@login_required
def viewInbox(request):

	inbox = UserInbox.objects.filter(username__username__exact=request.user.username)[0].feedItem.all()
	return render_to_response('inbox/index.html', locals())

@login_required
def shareFeed_view(request):
    pass

@login_required
def shareStory_view(request, story_uuid):

    c = {}
    c.update(csrf(request))

    friends = request.user.get_profile().friends.all()

    if request.method == 'POST':
        form = ShareStoryForm(friends, request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            for item in cd['friends_choice']:
                print UserProfile.objects.filter(user_uuid__exact=item)[0].user.email

            return HttpResponseRedirect('/story/shared')
    else:
        form = ShareStoryForm(friends)

    return render_to_response('sharestory.html', locals(), context_instance=RequestContext(request))

@login_required
def subscribeFeed_view(request, feed_uuid):

    c = {}
    c.update(csrf(request))

    username = request.user.username
    user = User.objects.get(username=username)
    profile = user.profile

    categories = []
    for c in profile.categories.all().order_by('name'):
        categories.append(c.name)

    if request.method == 'POST':
        form = SubscribeFeedForm(categories, request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            task_subscribeFeed.delay(user=user, feed_uuid=feed_uuid, category_name=cd['category_choice'])
            return HttpResponseRedirect('/feed/thanks')
    else:
        form = SubscribeFeedForm(categories, initial={'category': 'Uncategorized'})

    return render_to_response('subscribefeed.html', locals(), context_instance=RequestContext(request))

@login_required
def editFeed_view(request, feed_uuid):

    c = {}
    c.update(csrf(request))

    username = request.user.username
    user = User.objects.get(username=username)
    profile = user.profile

    userFeed = profile.feeds.filter(feed__site_uuid__exact=feed_uuid)[0]
    feed_name = userFeed.feed.name

    categories = []
    for c in profile.categories.all().order_by('name'):
        categories.append(c.name)

    if request.method == 'POST':
        form = EditFeedForm(categories, request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            return HttpResponseRedirect('/feed/thanks')
    else:
        initial_data = {'category': userFeed.category.name, 'feed_name': feed_name}
        form = EditFeedForm(categories, initial=initial_data)

    return render_to_response('editfeed.html', locals(), context_instance=RequestContext(request))

@login_required
def addFeed_view(request):

    c = {}
    c.update(csrf(request))

    username = request.user.username
    user = User.objects.get(username=username)
    profile = user.profile

    categories = []
    for c in profile.categories.all().order_by('name'):
        categories.append(c.name)

    if request.method == 'POST':
        form = AddFeedForm(categories, request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if cd['subscribe']:
                task_addFeed.delay(FeedStaging(url=cd['url'], user=username, category=cd['category']))
            else:
                task_addFeed.delay(FeedStaging(url=cd['url']))

            return HttpResponseRedirect('/feed/thanks')
    else:

        form = AddFeedForm(categories, initial={'category': 'Uncategorized'})

    return render_to_response('addfeed.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def addCategory_view(request):

    c = {}
    c.update(csrf(request))

    user = request.user.username

    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            task_addCategory.delay(user=user, category=cd['category'])

            return HttpResponseRedirect('/category/submitted')
    else:

        form = AddCategoryForm()

    return render_to_response('addcategory.html', {'form': form}, context_instance=RequestContext(request))

def storyShared(request):
	return render_to_response('storyshared.html')
	
def categorySubmitted(request):
	return render_to_response('categorySubmitted.html')
	
def feedThanks(request):
	return render_to_response('feedThanks.html')
	
def search(request):
	error = False
	if 'q' in request.GET:
		q = request.GET['q']
		if not q:
			error = True
		else:
			news = FeedItem.objects.filter(title__icontains=q).order_by('-updatedDate')
			return render_to_response('search_results.html',
				{'news': news, 'query': q})

	return render_to_response('search_form.html', {'error': error})

def simple_ajax_search(request):
	error = False
	ret = {}
	if 'q' in request.POST:
		q = request.POST['q']
		if q:
			news = FeedItem.objects.filter(title__icontains=q).order_by('-updatedDate')
			ret['results'] = news
		else:
			ret['success'] = False
	return ret

def grab_feed(request, site_uuid):
	error = False
	ret = {}

	if site_uuid:
		
		site = Feed.objects.filter(site_uuid=site_uuid)[0]
		d = site.next_update - datetime.now()

		if site.logo:
			site_logo = site.logo
		else:
			site_logo = ""

		ret['nextUpdate'] = (d.seconds * 1000)

		latest_news = []
		for item in FeedItem.objects.filter(site=site).order_by('-addedDate').annotate()[:10]:

			summary = re.sub(r'<[^>]*?>', '', item.summary)
			if len(summary) > 300:
				summary = summary[:300] + "[...]"

			latest_news.append({"uuid": item.story_uuid, "title": item.title, "summary": summary, "url": item.url, "logo": site_logo})

		ret['results'] = latest_news
		ret['success'] = True

	else:
		ret['success'] = False

	return json_response(ret)

def site_login(request):

    c = {}
    c.update(csrf(request))

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            # Fail
            pass
    else:
        pass
        # Invalid

def site_logout(request):

    c = {}
    c.update(csrf(request))

    if request.user is not None:
        if request.user.is_active:
            logout(request)
            return HttpResponseRedirect('/')
        else:
            # Fail
            # Fix this!
            pass
    else:
        pass
        # Invalid
        # Fix this!

def site_register(request):

    c = {}
    c.update(csrf(request))

def add_fb_instance(request):
    # if already has a facebook instance, immediately return
    if getattr(request, 'facebook', None) is not None:
     return request
    # auth_token is other important possible param
    api_key = settings.FACEBOOK_API_KEY
    secret_key = settings.FACEBOOK_SECRET_KEY
    app_name = getattr(settings, 'FACEBOOK_APP_NAME', None)
    callback_path = getattr(settings, 'FACEBOOK_CALLBACK_PATH', None)
    internal = getattr(settings, 'FACEBOOK_INTERNAL', True)
    request.facebook = facebook.Facebook(
        api_key=api_key,
        secret_key=secret_key,
        app_name=app_name,
        callback_path=callback_path,
        internal=internal
    )

def require_fb_login(request, next=None):
    if getattr(request, 'facebook', None) is None:
        add_fb_instance(request)
    fb = request.facebook
    if not fb.check_session(request):
        return fb.redirect(fb.get_login_url(next=next))

def test_facebook(request):
    add_fb_instance(request)
    redirect = require_fb_login(request)

    if redirect is not None: return redirect

    user = get_fb_user(request.facebook)


