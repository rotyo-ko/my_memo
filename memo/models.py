import pykakasi
from django.db import models
from django.utils.text import slugify
from django.conf import settings


kks = pykakasi.kakasi()
def generate_slug(title, user_id):
    """日本語からローマ字を生成してslugにする関数"""
    # slugifiyはallow_unicode=False がデフォルトで日本語だと空文字をかえす
    # "テスト1"の時はslugify()だけだと1とかえしてしまうのでpykakasiでローマ字変換してslugを生成する
    try:
        result = kks.convert(title)
        romaji = "".join([item['hepburn'] for item in result])
        slug = slugify(romaji, allow_unicode=False)
        if not slug:
            raise ValueError("slugが空です")
    except Exception:
        # 空文字の時はmemo-<ユーザーid>としてslugを生成する
        slug = f"memo-{user_id}"
    return slug


class Memo(models.Model):
    CATEGORY = [
        ("work", "仕事"),
        ("personal", "個人"),
        ("study", "勉強"),
        ("hobby", "趣味"),
        ("other", "その他")
    ]
       
    PRIORITY_CHOICES = [
        (1, "低"),
        (2, "中"),
        (3, "高"),
    ]
    
    title = models.CharField(verbose_name="タイトル", max_length=20,)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    priority = models.IntegerField(verbose_name="重要度", choices=PRIORITY_CHOICES, default=2)
    category = models.CharField(verbose_name="カテゴリー", choices=CATEGORY, default="personal", max_length=20)
    content = models.TextField(verbose_name="メモ内容")
    created_at = models.DateTimeField(verbose_name="作成日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True)
    slug = models.SlugField(verbose_name="URL用文字列", max_length=255, blank=True)
    # slugを導入
    # saveで重複を避けるようにするのでunique=True,unique_togetherは使わない。
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """titleからslugを生成。重複した場合は数字で対応"""
        if not self.slug:
            base_slug = generate_slug(self.title, self.user.id)
            slug = base_slug
            i = 1        
            # titleが重複したときは数字を足してslugを生成する
            while Memo.objects.filter(
                user=self.user,
                slug=slug
                ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)