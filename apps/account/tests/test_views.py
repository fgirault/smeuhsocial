# -*- encoding: utf-8 -*-
from smeuhoverride.tests import BaseTestCase
from django.contrib.auth.models import User


class TestResetPassword(BaseTestCase):

    def test_post(self):
        from emailconfirmation.models import EmailAddress
        user = User.objects.create_user('foo', password='secret',
                                        email='foo@example.com')
        EmailAddress.objects.create(user=user, email=user.email, verified=True)
        response = self.client.post('/account/password_reset/',
                                    {'email': user.email}, follow=True)
        self.assertContains(response, u"Nous vous avons envoyé un email")

