from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import TestCase

try:
    from mock import Mock, patch
except ImportError:
  raise ImportError("Mock is a requirement for la_facebook tests")


from la_facebook.models import UserAssociation
from la_facebook.access import OAuthAccess, OAuth20Token

# Mocking setup
mock_check_token = Mock()
mock_check_token.return_value = OAuth20Token("dummytokentext", 55555)
mock_access_callback = Mock()
mock_access_callback.return_value = HttpResponse("mock callback called")

class BasicViews(TestCase):


    def test_la_facebook_login(self):
        """ Django test client does not let us http off
                our server. So we just look for the right
                pointers to the facebook site
        """

        url = reverse('la_facebook_login')

        # we have 302?
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # Now check on the location header passed to the browser
        location = response._headers['location'][1]

        # Are we going to the right location?
        self.assertTrue("https://graph.facebook.com/oauth/authorize" in location)

        # Is the facebook APP ID in the location header?
        app_id = settings.FACEBOOK_ACCESS_SETTINGS['FACEBOOK_APP_ID']
        self.assertTrue(location.endswith(app_id))

    def test_facebook_callback_failure(self):
        """
        This only supports failure.

        """
        url = reverse('la_facebook_callback')
        response = self.client.get(url)
        self.assertContains(response, "OAuth Error: token_mismatch")

    # need to patch the check_token function so does not make api call
    @patch('la_facebook.views.OAuthAccess.check_token', mock_check_token)
    # patch the callback itself, we are just testing the view
    @patch('la_facebook.views.OAuthAccess.callback', mock_access_callback)
    def test_facebook_callback(self):
        """
        check that a http response is returned
        since we are mocking the callback, we return a response instead of
        redirect
        """

        url = reverse('la_facebook_callback')
        params = {
                'code': u'2._8B6KX_iW8zKVM_IAkvc6g__.3600.1298995200-529648811|H_Hp_gGrqPayUlDYdwtJuq49PLg',
                'client_secret': 'cdd60917e6a30548b933ba91c48289bc',
                'redirect_uri': u'http://localhost:8000/la_facebook/callback',
                'client_id': '124397597633470'
                }
        response = self.client.get(url,data=params)
        self.assertEquals(response.content, "mock callback called")
        self.assertTrue(mock_access_callback.called)


