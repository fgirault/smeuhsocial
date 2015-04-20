from smeuhoverride.tests import BaseTestCase


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

