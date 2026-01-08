from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import Memo


class MemoAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", nickname="nickname", password="password")
        self.memo = Memo.objects.create(
            user = self.user,
            title="test_title",
            content="test_content",
            )
        self.client.login(username="user", password="password")

    def test_get_memo(self):
        res = self.client.get("/api/memo/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], "test_title")
        self.assertEqual(res.data["results"][0]["content"], "test_content")
        self.assertEqual(res.data["results"][0]["slug"], self.memo.slug)
        # デフォルト値を確認
        self.assertEqual(res.data["results"][0]["priority"], 2)
        self.assertEqual(res.data["results"][0]["category"], "personal")
    
    def test_get_memo_id(self):
        res = self.client.get(f"/api/memo/{self.memo.pk}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "test_title")
        self.assertEqual(res.data["content"], "test_content")
        self.assertEqual(res.data["id"], self.memo.pk)
        # デフォルト値を確認
        self.assertEqual(res.data["priority"], 2)
        self.assertEqual(res.data["category"], "personal")

    def test_get_memo_pagination(self):
        # ページネーションがきいているかチェック
        for i in range(5):
            Memo.objects.create(
                user=self.user,
                title=f"test_title_{i}",
                content=f"test_content_{i}",
            )
        res = self.client.get("/api/memo/")
        self.assertEqual(res.status_code, 200)
        # setUpと合わせてデータは6個あるはず
        # ページネーションが有効であれば5個ずつ表示される
        # 最後に作ったMemoオブジェクトが先頭にくることを確認
        self.assertEqual(len(res.data["results"]), 5)
        self.assertEqual(res.data["results"][0]["title"], "test_title_4")
        self.assertEqual(res.data["results"][0]["content"], "test_content_4")
        res = self.client.get("/api/memo/?page=2")
        # 2ページ目は1件だけ表示される
        # ordering = ["-priority", "-updated_at", "-created_at"]
        # なのでこの場合 一番最初に作ったself.memoが最後になる
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["title"], "test_title")
        self.assertEqual(res.data["results"][0]["content"], "test_content")

    def test_get_memo_without_login(self):
        self.client.logout()
        res = self.client.get("/api/memo/")
        self.assertIn(res.status_code, [401, 403])
        
    def test_cannot_get_other_users_memo(self):
        User = get_user_model() 
        user = User.objects.create_user(username="other", password="password")
        other_memo = Memo.objects.create(user=user, title="other_title", content="other_content")
        res = self.client.get(f"/api/memo/{other_memo.pk}/")
        self.assertEqual(res.status_code, 404)
    
    
    def test_post_memo(self):
        res = self.client.post(
            "/api/memo/",
            data={"title": "post_title","content": "post_content"},
        ) # APIの場合リダイレクトはほぼ発生しないのでfollow=Trueはいらない
        
        self.assertEqual(res.status_code, 201)
        #self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data["title"], "post_title")
        self.assertEqual(res.data["content"], "post_content")
        self.assertEqual(res.data["user"], self.user.id)
    
    def test_post_memo_without_login(self):
        self.client.logout()
        res = self.client.post(
            "/api/memo/",
            data={"title": "post_title","content": "post_content"},
        )
        self.assertIn(res.status_code, [401, 403])
    
    def test_put_memo(self):
        res = self.client.put(
            f"/api/memo/{self.memo.pk}/",
            data={"title": "put_title", "content": "put_content"},
            format="json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "put_title")
        self.assertEqual(res.data["content"], "put_content")
    
    def test_put_memo_without_login(self):
        self.client.logout()
        res = self.client.put(
            f"/api/memo/{self.memo.pk}/",
            data={"title": "put_title", "content": "put_content"},
            format="json"
        ) # PUT はformat="json"を入れておいた方が安全
        self.assertIn(res.status_code, [401, 403])

    def test_delete_memo(self):
        res = self.client.delete(f"/api/memo/{self.memo.pk}/")
        # DELETEが成功すると204になる
        self.assertEqual(res.status_code, 204)
        memos = Memo.objects.filter(user=self.user)
        self.assertEqual(memos.count(), 0)
        
    def test_delete_memo_without_login(self):
        self.client.logout()
        res = self.client.delete(f"/api/memo/{self.memo.pk}/")
        self.assertIn(res.status_code, [401, 403])
        memos = Memo.objects.filter(user=self.user)
        self.assertEqual(memos.count(), 1)


class MemoAPITestValidation(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", nickname="nickname", password="password")
        self.memo = Memo.objects.create(user=self.user, title="title", content="content")
        self.client.login(username="user", password="password")
    
    def test_post_memo_without_title(self):
        res = self.client.post(
            "/api/memo/",
            data={"content": "post_content"},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("title", res.data)
        # "title"フィールドでエラーになっていることを確認

    def test_post_memo_without_content(self):
        res = self.client.post(
            "/api/memo/",
            data={"title": "post_title",},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("content", res.data)

    def test_post_memo_invalid_priority(self):
        res = self.client.post(
            "/api/memo/",
            data={"title": "post_title",
                  "content": "post_content",
                  "priority": "invalid"}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("priority", res.data)

    def test_post_memo_invalid_category(self):
        res = self.client.post(
            "/api/memo/",
            data={"title": "post_title",
                  "content": "post_content",
                  "category": "invalid"}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("category", res.data)

    def test_put_memo_invalid_data(self):
        res = self.client.put(
            f"/api/memo/{self.memo.pk}/",
            data={"title": "",
                  "content": "put_content"},
            format="json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("title", res.data)

    def test_post_memo_invalid_word(self):
        res = self.client.post(
            "/api/memo/",
            data={"title": "禁止ワード入り",
                  "content": "post_content"},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("title", res.data)



