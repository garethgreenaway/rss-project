from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from la_facebook.models import UserAssociation


class UserAssociationTests(TestCase):
    
    def setUp(self):
        self.user1 = User.objects.create(username='tester1',password="test")
        self.user1.save()
        self.user2 = User.objects.create(username='tester2',password="test")
        self.user2.save()
    
    def test_expired(self):
        """        return datetime.datetime.now() < self.expires    """
        ua_active = UserAssociation.objects.create(
                user=self.user1,
                identifier='12345',
                token='12345',
                expires=datetime.now() + timedelta(1)
        )
        ua_active.save()
        self.assertTrue(ua_active.expired())
        
        ua_expired = UserAssociation.objects.create(
                user=self.user2,
                identifier='54321',
                token='54321',
                expires=datetime.now() - timedelta(1)
        )
        ua_expired.save()
        self.assertFalse(ua_expired.expired())        
