"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.contrib.auth.models import User
from django.test import TestCase


class TestHomePage(TestCase):

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'Smeuh.org')


class SetMessageRemovedBugs(TestCase):

    def create_user(self, username='bob'):
        return User.objects.create_user(username, password='secret')

    def login(self, username):
        self.client.login(username=username, password='secret')

    def check_toggle_follow(self, action):

        me = self.create_user()
        her = self.create_user('alice')

        self.login(me.username)

        resp = self.client.post('/touites/toggle_follow/%s/' % her.username, {
            'action': action,
        }, follow=True)

        self.assertEqual(resp.status_code, 200)

    def test_follow(self):
        self.check_toggle_follow('follow')

    def test_unfollow(self):
        self.check_toggle_follow('unfollow')
