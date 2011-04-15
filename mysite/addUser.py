#!/usr/bin/env python

#
# Pull in the django support
#
from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.contrib.auth.models import User
from browseFeeds.models import Category, UserProfile
from django.db import connection
from datetime import date

import getopt
import hashlib
import sys

def generate_uuid(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()

def usage():
        print """
Usage: addFeed.py options

Options:
        -h, --help      Show this message
        -u, --user	    Username
        -p, --password	Password
        -r, --real      Real Name
        -e, --email     Email Address
"""


try:
	opts, args = getopt.gnu_getopt(sys.argv[1:], "u:p:r:e:h", ["user=", "password=", "real=","help"])
except getopt.GetoptError, err:

	print str(err)
    	usage()
       	sys.exit(2)

user = None
tag = None
urls = []

for o, a in opts:

	if o in ("-p", "--password"):
		password = a

	elif o in ("-u", "--user"):
		username = a

	elif o in ("-e", "--email"):
		email = a

	elif o in ("-r", "--real"):
		realname = a


print "Adding %s" % (username)

if not User.objects.filter(username__exact=username):
    user = User.objects.create_user(username, email, password)
    user.save()


else:
    user = User.objects.filter(username__exact=username)[0]

profile = user.profile
profile.user_uuid = generate_uuid(email)

category = Category.objects.create(name="Uncategorized")
profile.categories.add(category)

profile.save()
