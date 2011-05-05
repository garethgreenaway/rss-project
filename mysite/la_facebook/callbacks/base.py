import urlparse

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.db.models import get_model
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.conf import settings

from la_facebook.la_fb_logging import logger


class BaseFacebookCallback(object):

    FACEBOOK_GRAPH_TARGET = "https://graph.facebook.com/me"
    FACEBOOK_GRAPH_FRIENDS_TARGET = FACEBOOK_GRAPH_TARGET + "/friends"

    def __call__(self, request, access, token):

        print request.user
        if not request.user.is_authenticated():
            logger.debug("BaseFacebookCallback.__call__:'\
                    ' request.user not authenticated")
            self.authenticated = False
            user_data = self.fetch_user_data(request, access, token)
            user = self.lookup_user(request, access, user_data)
            if user is None:
                logger.debug("BaseFacebookCallback.__call__:'\
                 ' no existing django user found for this facebook identifier")
                ret = self.handle_no_user(request, access, token, user_data)
                # allow handle_no_user to create a user if need be
                if isinstance(ret, User):
                    logger.debug("BaseFacebookCallback.__call__:'\
                            self.handle_no_user returned valid django user")
                    user = ret
            else:
                logger.debug("BaseFacebookCallback.__call__:'\
                   existing django user found for this facebook identifier")
                ret = self.handle_unauthenticated_user(request, user, access, 
                        token, user_data)
            if isinstance(ret, HttpResponse):
                return ret
        else:
            logger.debug("BaseFacebookCallback.__call__:'\
                    request.user is authenticated")
            self.authenticated = True
            user = request.user
            user_data = self.fetch_user_data(request, access, token)
            self.create_profile(request, access, token, user)
            self.persist(user, token, user_data)

        redirect_to = self.redirect_url(request)
        logger.debug("redirecting to: %s" % redirect_to)

        return redirect(redirect_to)

    def fetch_user_data(self, request, access, token):
        raise NotImplementedError(
                "Callbacks must have a fetch_user_data method")

    def lookup_user(self, request, access, user_data):
        raise NotImplementedError("Callbacks must have a lookup_user method")

    def redirect_url(self, request, fallback_url=settings.LOGIN_REDIRECT_URL, 
            redirect_field_name="next", session_key_value="redirect_to"):
        """
        Returns the URL to be used in login procedures by looking at different
        values in the following order:

        - a REQUEST value, GET or POST, named "next" by default.
        - LOGIN_REDIRECT_URL - the URL in the setting
        - LOGIN_REDIRECT_URLNAME - the name of a URLconf entry in the settings
        """

        redirect_to = request.REQUEST.get(redirect_field_name)
        if not redirect_to:
            logger.debug("redirect not in get params")
            # try the session if available
            if hasattr(request, "session"):
                redirect_to = request.session.get(session_key_value)
                if not redirect_to:
                    # Should fix this at some point
                    logger.debug("no redirect found, using fallback")
                    redirect_to = fallback_url
                # Heavier security check -- don't allow redirection to a different host.
                netloc = urlparse.urlparse(redirect_to)[1]
                if netloc and netloc != request.host:
                    logger.warning("redirect_to host does not match orgin")
                    redirect_to = fallback_url
        if not redirect_to:
            logger.debug("no redirect found, using fallback")
            redirect_to = fallback_url
        return redirect_to

    def handle_no_user(self, request, access, token, user_data):
        raise NotImplementedError("Callbacks must have a handle_no_user method")

    def handle_unauthenticated_user(
            self, request, user, access, token, user_data):
        raise NotImplementedError("Callbacks must have a '\
                'handle_unauthenticated_user method")

    def identifier_from_data(self, data):
        return "%s-%s" % (slugify(data['name']), data['id'])

