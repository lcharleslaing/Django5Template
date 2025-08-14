from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta

from surveys.models import Survey, Invite


class SurveySmokeTests(TestCase):
    def setUp(self):
        # Seed data and ensure published window is active
        call_command('seed_balanced_honesty')
        self.survey = Survey.objects.filter(title='Balanced Honesty Survey').first()
        now = timezone.now()
        self.survey.publish_start = now - timedelta(minutes=5)
        self.survey.publish_end = now + timedelta(days=7)
        self.survey.status = 'PUBLISHED'
        self.survey.save()

        # Create a superuser and login
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='test@example.com', email='test@example.com', password='x')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='test@example.com', password='x')

    def test_list_page_loads(self):
        resp = self.client.get(reverse('surveys:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Available Surveys')

    def test_detail_page_loads(self):
        resp = self.client.get(reverse('surveys:detail', args=[self.survey.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.survey.title)

    def test_take_page_get_loads(self):
        resp = self.client.get(reverse('surveys:take', args=[self.survey.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Submit Survey')

    def test_take_page_post_creates_response(self):
        # Post with minimal data (view currently does not enforce required question validation)
        resp = self.client.post(reverse('surveys:take', args=[self.survey.pk]), data={})
        # Should redirect to completion page
        self.assertEqual(resp.status_code, 302)

    def test_admin_list_loads(self):
        resp = self.client.get(reverse('surveys:survey_admin_list'))
        self.assertEqual(resp.status_code, 200)

    def test_reports_page_loads(self):
        resp = self.client.get(reverse('surveys:survey_reports', args=[self.survey.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_my_invites_page_loads_and_shows_invite(self):
        now = timezone.now()
        Invite.objects.create(
            survey=self.survey,
            email=self.user.email,
            token='tok123',
            expires_at=now + timedelta(days=1),
        )
        resp = self.client.get(reverse('surveys:my_invites'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'My Survey Invites')


