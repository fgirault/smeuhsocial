# -*- encoding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from avatar.models import Avatar

from messages.models import Message
from blog.models import Post


class BaseTestCase(TestCase):

    def setUp(self):
        self.me = self.create_user('bob')
        self.login(self.me.username)
        self.her = self.create_user('alice')

    def create_user(self, username='bob'):
        return User.objects.create_user(username, password='secret')

    def login(self, username):
        self.client.login(username=username, password='secret')


class TestHomePage(BaseTestCase):

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'Homepage')


class TestTouites(BaseTestCase):

    def check_toggle_follow(self, action):

        self.login(self.me.username)

        resp = self.client.post(
            '/touites/toggle_follow/%s/' % self.her.username, {
                'action': action,
            }, follow=True)

        self.assertEqual(resp.status_code, 200)

    def test_follow(self):
        self.check_toggle_follow('follow')

    def test_unfollow(self):
        self.check_toggle_follow('unfollow')

    def test_post(self):
        response = self.client.post("/touites/post/", {
            'text': 'Touite Content'
        }, follow=True)
        self.assertContains(response, 'Touite Content')

    def test_get_list_no_param(self):
        response = self.client.get("/touites/")
        self.assertNotContains(response, "None")

    def test_get_list_with_reply_param(self):
        response = self.client.get("/touites/?reply=alice")
        self.assertContains(response, "@alice")


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
        response = self.client.post('/%s/' % self.her.username, {
            'to_user': self.her.username,
            'action': u'invite',
            'message': u"Let's be friends!",
        }, follow=True)

        self.assertContains(
            response,
            "Friendship requested with %s" % self.her.username)


class TestInvite(BaseTestCase):

    def test_invite_new_user(self):
        resp = self.client.post('/invitations/invite/', {
            'email': 'somebody@example.com',
            'message': 'Message body',
        }, follow=True)

        self.assertContains(
            resp,
            'Invitation to join sent to somebody@example.com')


class BaseImageTest(BaseTestCase):
    from os.path import join, dirname
    testfile = join(dirname(dirname(dirname(__file__))), 'tests', '1px.gif')


class TestAvatar(BaseImageTest):

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
            'choice': Avatar.objects.get().pk,
        }, follow=True)
        self.assertContains(resp, 'Successfully updated')

    def test_delete_avatar(self):
        self.upload_avatar()
        resp = self.client.post('/avatar/delete/', {
            'choices': [Avatar.objects.get().pk],
        }, follow=True)
        self.assertContains(resp, 'Successfully deleted')


class TestPhoto(BaseImageTest):

    def test_photo_details(self):
        title = "A cool photo"
        resp = self.client.post('/photos/upload/', {
            'image': open(self.testfile),
            'title': title,
            'safetylevel': 1,
            'action': 'upload',
        }, follow=True)

        self.assertContains(resp, title)


class TestResetPassword(BaseTestCase):

    def test_post(self):
        from emailconfirmation.models import EmailAddress
        user = User.objects.create_user('foo', password='secret',
                                        email='foo@example.com')
        EmailAddress.objects.create(user=user, email=user.email, verified=True)
        response = self.client.post('/account/password_reset/',
                                    {'email': user.email}, follow=True)
        self.assertContains(response, u"Nous vous avons envoyé un email")


class TestBlog(BaseTestCase):

    def create_post(self):
        return Post.objects.create(title=u"A Neat Title", slug="the-slug",
                                   author=self.me, body="Some content")

    def test_view_post(self):
        self.create_post()
        response = self.client.get("/bob/blog/the-slug")
        self.assertContains(response, "Some content")

    def test_view_source(self):
        self.create_post()
        response = self.client.get("/bob/blog/the-slug/source")
        self.assertContains(response, "Some content")

    def test_blogs_feed(self):
        self.create_post()
        response = self.client.get("/feeds/blogs/")
        self.assertEqual(response.status_code, 200)

    def test_user_blog_feed(self):
        self.create_post()
        response = self.client.get("/{}/blog/feed/".format(self.me.username))
        self.assertEqual(response.status_code, 200)


class TestEditProfile(BaseTestCase):

    def test_get_edit_profile(self):
        response = self.client.get("/profiles/edit/")
        self.assertContains(response, "bob")
