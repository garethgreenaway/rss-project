import datetime
from django.test import TestCase

try:
  from mock import Mock, patch
except ImportError:
  raise ImportError("Mock is a requirement for la_facebook tests")

try:
    from django.test.client import RequestFactory
except ImportError:
    raise ImportError("callback tests require Django > 1.3 for RequestFactory")

from django.contrib.auth.models import User, AnonymousUser

from la_facebook.access import OAuthAccess, OAuth20Token
from la_facebook.callbacks.base import BaseFacebookCallback
from la_facebook.callbacks.default import DefaultFacebookCallback
# from la_facebook.la_fb_logging import logger
from la_facebook.models import UserAssociation

factory = RequestFactory()

mock_fetch_user_data = Mock()
mock_fetch_user_data.return_value = {'id':'facebookid','color':'red'}


class BaseCallbackTests(TestCase):

    urls = 'la_facebook.tests.urls'

    def setUp(self):
        # logger.debug("callback test case setup")
        self.request = factory.get('/callback',data={'next':'dummy'})
        test_user = User()
        test_user.username = 'test'
        test_user.save()
        self.request.user = test_user
        assoc = UserAssociation()
        assoc.user = test_user
        assoc.token = 'facebooktokenstring'
        assoc.expires = datetime.datetime.now() + datetime.timedelta(1)
        assoc.save()
        self.token = OAuth20Token(assoc.token, 5555)
        self.access = OAuthAccess()

    def test_call(self):
        basecallback = BaseFacebookCallback()
        ret = basecallback(self.request, self.access, self.token)
        self.assertEquals(ret.status_code, 302)
        # logger.debug(str(ret._headers['location'][1]))
        self.assertEquals(ret._headers['location'][1], '/dummy' )

    def test_redirect_url(self):
        callback = BaseFacebookCallback()
        resp = callback.redirect_url(self.request)
        self.assertEquals(resp,'dummy')

    def test_identifier_from_data(self):
        callback = BaseFacebookCallback()
        data = {'name':'test name','id':'testid'}
        resp = callback.identifier_from_data(data)
        self.assertEquals(resp,'test-name-testid')

 # Boilerplated, only tests that # of args not changed in regression:

    def test_fetch_user_data(self):
        callback = BaseFacebookCallback()
        self.assertRaises(NotImplementedError,callback.fetch_user_data,
                'arg','arg','arg')

    def test_lookup_user(self):
        callback = BaseFacebookCallback()
        self.assertRaises(NotImplementedError,callback.lookup_user,
                'arg','arg','arg')

    def test_handle_no_user(self):
        callback = BaseFacebookCallback()
        self.assertRaises(NotImplementedError,callback.handle_no_user,
                'arg','arg','arg','arg')

    def test_handle_unauthenticated_user(self):
        callback = BaseFacebookCallback()
        self.assertRaises(NotImplementedError,callback.handle_unauthenticated_user,
                'arg','arg','arg','arg','arg')


class DefaultCallbackTests(TestCase):

    urls = 'la_facebook.tests.urls'

    def setUp(self):
        # logger.debug("callback test case setup")
        self.request = factory.get('/callback',data={'next':'dummy'})
        test_user = User()
        test_user.username = 'test'
        test_user.save()
        self.test_user = test_user
        self.anon_user = AnonymousUser()
        self.request.user = test_user
        assoc = UserAssociation()
        assoc.user = test_user
        assoc.token = 'facebooktokenstring'
        assoc.identifier = 'facebookid'
        assoc.expires = datetime.datetime.now() + datetime.timedelta(1)
        assoc.save()
        self.token = OAuth20Token(assoc.token, 5555)
        self.access = OAuthAccess()

    def test_lookup_user_exists(self):
        callback = DefaultFacebookCallback()
        user = callback.lookup_user(self.request, self.access,{'id':'facebookid'})
        self.assertEquals(user, self.test_user)

    def test_lookup_user_does_not_exist(self):
        callback = DefaultFacebookCallback()
        user = callback.lookup_user(self.request, self.access,{'id':'bad-id'})
        self.assertEquals(user,None)

    @patch(
       'la_facebook.callbacks.default.DefaultFacebookCallback.fetch_user_data',
       mock_fetch_user_data)
    def test_update_profile_from_graph(self):
        callback = DefaultFacebookCallback()
        class DummyProfile(object):
            def __init__(self):
                self.color = "blue"
        profile = DummyProfile()
        ret_p = callback.update_profile_from_graph(self.request, self.access,
                self.token, profile)
        self.assertEquals(ret_p.color,'red')

    @patch(
       'la_facebook.callbacks.default.DefaultFacebookCallback.fetch_user_data',
       mock_fetch_user_data)
    def test_fectch_user_data(self):
        callback = DefaultFacebookCallback()
        ud = callback.fetch_user_data(self.request, self.access, 'faketoken')
        self.assertEquals(ud['id'], 'facebookid')

    @patch(
       'la_facebook.callbacks.default.DefaultFacebookCallback.fetch_user_data',
       mock_fetch_user_data)
    def test_handle_no_user(self):
        """
        This is a complex functional/integration test, hitting the following:
            create_user
                identifier_from_data
                create_profile
                    update_profile_from_graph
                handle_unauthenticated_user
                    login_user
                    persist
        """
        class session_like_obj(dict):
            # an alternative to http://code.djangoproject.com/ticket/10899
            def __init__(self):
                dict.__init__(self)
                self['_auth_user_id'] = 'notme'
                self.flush = lambda: True
                self.set_expiry = Mock()
        pseudo_session = session_like_obj()
        self.request.session = pseudo_session
        callback = DefaultFacebookCallback()
        user_data = {'name':'new_user','id':'newfacebookid'}
        resp = callback.handle_no_user(self.request, self.access, self.token,
                user_data)
        ident = callback.identifier_from_data(user_data)
        expected_user = User.objects.get(username=ident)
        # was the expected user created and returned
        self.assertEquals(resp,expected_user)
        # was the set_expiry method called on the session
        # could check expected date also
        self.assertTrue(pseudo_session.set_expiry.called)
        # check that user data was persisted
        assoc_obj = UserAssociation.objects.get(identifier=user_data['id'])
        self.assertEquals(self.token.expires, assoc_obj.expires)
