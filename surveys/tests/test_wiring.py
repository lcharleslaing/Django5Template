from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model


class WiringTests(TestCase):
    def test_surveys_url_included(self):
        User = get_user_model()
        u = User.objects.create_user(username='u@example.com', email='u@example.com', password='x')
        self.client.login(username='u@example.com', password='x')
        url = reverse('surveys:list')
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (200, 302))


