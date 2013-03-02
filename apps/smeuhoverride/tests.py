"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.contrib.auth.models import User
from django.test import TestCase

from messages.models import Message

class TestHomePage(TestCase):

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'Smeuh.org')


class BaseTestCase(TestCase):
    
    def setUp(self):
        self.me = self.create_user('bob')
        self.login(self.me.username)
        self.her = self.create_user('alice')

    def create_user(self, username='bob'):
        return User.objects.create_user(username, password='secret')

    def login(self, username):
        self.client.login(username=username, password='secret')


class TestTouites(BaseTestCase):

    def check_toggle_follow(self, action):

        self.login(self.me.username)

        resp = self.client.post('/touites/toggle_follow/%s/' % self.her.username, {
            'action': action,
        }, follow=True)

        self.assertEqual(resp.status_code, 200)

    def test_follow(self):
        self.check_toggle_follow('follow')

    def test_unfollow(self):
        self.check_toggle_follow('unfollow')


class TestMessages(BaseTestCase):

    def create_message(self):
        message = Message(sender=self.her, recipient=self.me,
                          subject='Subject Text', body='Body Text')
        message.save()
        return message

    def test_reply(self):
        message = self.create_message()
        self.client.post('/messages/reply/%s/' % message.pk, {
            'body': 'Reply body',
            'recipient': message.sender.username,
            'subject': 'Re: Subject Text',
        })

    def test_delete(self):
        message = self.create_message()
        self.client.post('/messages/delete/%s/' % message.pk, {
            'body': 'Reply body',
            'recipient': message.sender.username,
            'subject': 'Re: Subject Text',
        })

    def test_compose(self):
        self.client.post('/messages/compose/', {
            'body': 'Message body',
            'recipient': self.her.username,
            'subject': 'Subject text',
        })


class TestFriends(BaseTestCase):

    def test_invite(self):
        resp = self.client.post('/%s/' % self.her.username, {
            'to_user': self.her.username,
            'action': u'invite',
            'message': u"Let's be friends!",
        })

        self.assertContains(resp, "Friendship requested with %s" %
                self.her.username)


class TestInvite(BaseTestCase):

    def test_invite_new_user(self):
        resp = self.client.post('/invitations/invite/', {
            'email': 'somebody@example.com',
            'message': 'Message body',
        }, follow=True)

        self.assertContains(resp, 'Invitation to join sent to somebody@example.com')


class TestAvatar(BaseTestCase):
    from os.path import join, dirname
    testfile = join(dirname(dirname(dirname(__file__))), 'tests', '1px.gif')

    def upload_avatar(self):
        return self.client.post('/avatar/change/', {
            'avatar': open(self.testfile),
        }, follow=True)

    def test_upload_avatar(self):
        resp = self.upload_avatar()
        self.assertContains(resp, 'Successfully uploaded a new avatar')

    def test_change_avatar(self):
        self.upload_avatar()
        resp = self.client.post('/avatar/change/', {
            'choice': 1,
        }, follow=True)
        self.assertContains(resp, 'Successfully updated')

    def test_delete_avatar(self):
        self.upload_avatar()
        resp = self.client.post('/avatar/delete/', {
            'choices': [1],
        }, follow=True)
        self.assertContains(resp, 'Successfully deleted')
