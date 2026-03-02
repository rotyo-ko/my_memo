from rest_framework.test import APITestCase
from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Memo

class TestSummarizeAPIThrottle(APITestCase):
    """API のthrottleのテスト"""
    @patch("memo.api_views.summarize")
    def test_throttle_limit(self, mock_summarize):
        mock_summarize.return_value = "dummy_summarize"

        url = reverse("summarize")

        for _ in range(5):
            res = self.client.post(url, data={"text": "test"})
            self.assertEqual(res.status_code, 200)
        res = self.client.post(url, data={"text": "test"})
        self.assertEqual(res.status_code, 429)

class TestSummarizeThrottle(TestCase):
    """view のratelimitのテスト"""
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="テスト1", nickname="nickname", password="test1")
        self.client.login(username="テスト1", password="test1")
        self.memo = Memo.objects.create(title="test1", content="test_message", user=self.user)

    @patch("memo.views.Memo.generate_summary")
    def test_views_throttle(self, mock_summary):
        mock_summary.return_value = "dummy_summary"
        url = reverse("memo:detail", kwargs={"slug":self.memo.slug})

        for _ in range(5):
            res = self.client.post(url)
            self.assertEqual(res.status_code, 302)
        res = self.client.post(url)
        self.assertEqual(res.status_code, 403)