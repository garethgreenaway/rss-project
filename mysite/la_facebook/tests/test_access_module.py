from django.conf import settings
from django.test import TestCase
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from la_facebook.access import OAuthAccess
from la_facebook.utils.loader import load_path_attr
from la_facebook.exceptions import FacebookSettingsKeyError


class MissingKeySetting(TestCase):

    def setUp(self):
        try:
            self.app_id = settings.FACEBOOK_ACCESS_SETTINGS["FACEBOOK_APP_ID"]
            del(settings.FACEBOOK_ACCESS_SETTINGS["FACEBOOK_APP_ID"])
        except (ImproperlyConfigured, KeyError):
            # already missing from settings
            pass

    def test_key_not_in_settings(self):
        # instantiating OAuth will access property
        self.assertRaises(FacebookSettingsKeyError,OAuthAccess)

    def tearDown(self):
        settings.FACEBOOK_ACCESS_SETTINGS["FACEBOOK_APP_ID"] = self.app_id

class MissingFacebookSettings(TestCase):
    """check that missing settings dict throws AttributeError"""

    def setUp(self):
        try:
            print "setUp for MissingFacebookSettings"
            self.facebook_settings = settings.FACEBOOK_ACCESS_SETTINGS
            del(settings.FACEBOOK_ACCESS_SETTINGS)
        except (ImproperlyConfigured):
            # already missing from settings
            pass

    def test_facebook_settings_missing(self):
        self.assertRaises(AttributeError, OAuthAccess)

    def tearDown(self):
        settings.FACEBOOK_ACCESS_SETTINGS = self.facebook_settings


class PropertyTests(TestCase):

    def test_key_in_settings(self):
        # test if there is a key
        oauth = OAuthAccess()
        expected = settings.FACEBOOK_ACCESS_SETTINGS["FACEBOOK_APP_ID"]
        self.assertEquals(oauth.key, expected)


    def test_secret_in_settings(self):
        oauth = OAuthAccess()
        expected = settings.FACEBOOK_ACCESS_SETTINGS["FACEBOOK_APP_SECRET"]
        self.assertEquals(oauth.secret, expected)

    def test_access_token_url(self):
        oauth = OAuthAccess()
        access_token_endpoint = oauth.access_token_url
        expected_endpoints_url = "https://graph.facebook.com/oauth/access_token"
        self.assertEquals(access_token_endpoint,expected_endpoints_url)

    def test_authorize_url(self):
        oauth = OAuthAccess()
        authorize_url_endpoint = oauth.authorize_url
        expected_endpoint_url = "https://graph.facebook.com/oauth/authorize"
        self.assertEquals(authorize_url_endpoint,expected_endpoint_url)

    def test_provider_scope(self):
        oauth = OAuthAccess()
        provider_scope_endpoint = oauth.provider_scope
        expected_endpoint_url = None
        self.assertEquals(provider_scope_endpoint,expected_endpoint_url)

    def test_callback_url(self):
        oauth = OAuthAccess()
        callback_url = oauth.callback_url
        current_site = Site.objects.get(pk=settings.SITE_ID)
        base_url = "http://%s" % current_site.domain
        reversed_url = reverse("la_facebook_callback")
        expected_url = "%s%s" % (base_url, reversed_url)
        self.assertEquals(callback_url,expected_url)

    def test_callback(self):
        oauth = OAuthAccess()
        callback_endpoint = oauth.callback
        expected_callback_endpoint = load_path_attr(settings.FACEBOOK_ACCESS_SETTINGS["CALLBACK"])
        self.assertEquals(callback_endpoint,expected_callback_endpoint)

