from rest_framework import serializers
from .models import Memo


class MemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = ["id", "title", "priority", "category", "content", "summary", "created_at", "updated_at", "slug", "user"]
        read_only_fields = ["user", "summary", "slug"]

    def validate_title(self, value):
        """学習用に禁止ワードを設定 APIレスポンスは400になる"""
        if "禁止ワード" in value:
            raise serializers.ValidationError("禁止ワードが使用されています")
        return value
    
class SummarizeSerializer(serializers.Serializer):
    text = serializers.CharField(
        label="要約したい文章",
        help_text="ここに長い文章を入力してください（最大5000文字）",
        max_length=5000,
    )
    