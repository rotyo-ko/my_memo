from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from memo.models import Memo
from memo.forms import MemoForm


class TestMyMemoList(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="テスト1", nickname="nickname", password="test1")
        self.client.login(username="テスト1", password="test1")
        self.memo = Memo.objects.create(title="test1", content="test_message", user=self.user)
        

    def test_get(self):
        res = self.client.get(reverse("memo:memo"))
        self.assertTemplateUsed(res, "memo.html")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["object_list"][0].title, "test1")
        self.assertEqual(res.context["object_list"][0], self.memo)
        self.assertEqual(res.context["object_list"][0].user.nickname, "nickname")
        self.assertEqual(res.context["object_list"][0].category, "personal")
        self.assertEqual(res.context["object_list"][0].priority, 2)
        # slugをチェック
        self.assertEqual(res.context["object_list"][0].slug, "test1")
        # ニックネームが表示されているかテスト
        self.assertContains(res, "nickname")
    
    def test_get_slug_same_title(self):
        self.memo1 = Memo.objects.create(title="test1", content="test_message1", user=self.user)
        res = self.client.get(reverse("memo:memo"))
        self.assertTemplateUsed(res, "memo.html")
        # titleが重複したときのslugの確認
        slugs = [memo.slug for memo in res.context["object_list"]]
        # 順序を気にしないようにslug のリストを作ってからチェック
        self.assertIn("test1", slugs)
        self.assertIn("test1-1", slugs)
    
    def test_get_slug_pykakasi_and_slugify(self):
        # 日本語タイトルを用意,重複したときもここでテスト
        self.memo1 = Memo.objects.create(title="テスト1", content="test_message", user=self.user)
        self.memo2 = Memo.objects.create(title="テスト1", content="test_message_1", user=self.user)
        res = self.client.get(reverse("memo:memo"))
        self.assertTemplateUsed(res, "memo.html")
        slugs = [memo.slug for memo in res.context["object_list"]]
        self.assertIn("tesuto1", slugs)
        self.assertIn("tesuto1-1", slugs)

    def test_get_slug_without_pykakasi_and_slugify(self):
        # 記号のタイトルを作成し slug が memo-{user.id} になるかテストし、重複もテスト
        self.memo1 = Memo.objects.create(title="!!!", content="test_message", user=self.user)
        self.memo2 = Memo.objects.create(title="!!!", content="test_message", user=self.user)
        res = self.client.get(reverse("memo:memo"))
        self.assertTemplateUsed(res, "memo.html")
        slugs = [memo.slug for memo in res.context["object_list"]]
        self.assertIn(f"memo-{self.user.id}", slugs)
        self.assertIn(f"memo-{self.user.id}-1", slugs)

    def test_get_by_category(self):
        # カテゴリーごとにオブジェクトを取得できるかテスト
        self.memo1 = Memo.objects.create(title="work", category="work", content="test_message", user=self.user)
        self.memo2 = Memo.objects.create(title="study", category="study", content="test_message_1", user=self.user)
        self.memo3 = Memo.objects.create(title="work2", category="work", content="tes_message", user=self.user)
        res = self.client.get(reverse("memo:memo"), data={"category": "work"})
        self.assertTemplateUsed(res, "memo.html")
        
        memo_list = [memo for memo in res.context["object_list"]]
        self.assertEqual(len(memo_list), 2)
        self.assertIn(self.memo1, memo_list)
        self.assertIn(self.memo3, memo_list)

    def test_get_without_login(self):
        # ログインしていないときはログインページにリダイレクトされることを確認
        self.client.logout()
        res = self.client.get(reverse("memo:memo"))
        self.assertEqual(res.status_code, 302)
        


class TestMyMemoListPaginate(TestCase):
    def setUp(self):
        # Memoオブジェクトを20個作成
        User = get_user_model()
        self.user = User.objects.create_user(username="test", nickname="nickname", password="password")
        self.client.login(username="test", password="password")
        for i in range(20):
            Memo.objects.create(title=f"title_{i}", content="message", user=self.user)
        
    def test_get_with_paginate(self):
        res1 = self.client.get(reverse("memo:memo"))
        self.assertTemplateUsed(res1, "memo.html")
            
        # 1ページ目が9個表示されていることを確認
        self.assertEqual(len(res1.context["page_obj"]), 9)
        title_list = [memo.title for memo in res1.context["object_list"]]
        self.assertIn("title_19", title_list)
        self.assertIn("title_11", title_list)
        # paginate_orphans = 2　から2ページ目が11個表示されていることを確認
        res2 = self.client.get(reverse("memo:memo"), data={"page": 2})
        self.assertEqual(len(res2.context["object_list"]), 11)
        title_list2 = [memo.title for memo in res2.context["object_list"]]
        self.assertIn("title_2", title_list2)
        self.assertIn("title_10", title_list2)
        # 3ページ目でなく2ページ目に表示されているか確認
        self.assertIn("title_0", title_list2)
        self.assertIn("title_1", title_list2)

    def test_get_with_paginate_emptypage(self):
        res = self.client.get(reverse("memo:memo"), data={"page": 10})
        self.assertTemplateUsed(res, "memo.html")
        # 1ページ目が表示されることを確認
        self.assertEqual(len(res.context["object_list"]), 9)
        title_list = [memo.title for memo in res.context["object_list"]]
        self.assertIn("title_19", title_list)
        self.assertIn("title_11", title_list)

    


class TestMemoCreate(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="test", nickname="nickname", password="password")
        self.client.login(username="test", password="password")

    def test_get(self):
        res = self.client.get(reverse("memo:create"))
        self.assertTemplateUsed(res, "create.html")
        self.assertEqual(res.status_code, 200)
        # assertIsInstanceでMemoFormのインスタンスかを確認
        self.assertIsInstance(res.context["form"], MemoForm)

    def test_post(self):
        # category, priorityはデフォルト値をもってるがpostの時は書かないと成功しない。
        res = self.client.post(reverse("memo:create"), data={
            "title": "post",
            "content": "post_message",
            "category": "personal",
            "priority": 2
            }
        )
        self.assertRedirects(res, reverse("memo:memo"))
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Memo.objects.filter(user=self.user).exists())

    
    def test_post_without_login(self):
        self.client.logout()
        res = self.client.post(reverse("memo:create"), data={
            "title":"post",
            "content": "post_message",
            "category": "personal",
            "priority": 2
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Memo.objects.count(), 0)
        
        

    
            
    
        
        
        
        


