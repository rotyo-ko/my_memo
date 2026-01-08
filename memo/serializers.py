from rest_framework import serializers
from .models import Memo


class MemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = "__all__"
        read_only_fields = ["user"]

    def validate_title(self, value):
        """学習用に禁止ワードを設定 APIレスポンスは400になる"""
        if "禁止ワード" in value:
            raise serializers.ValidationError("禁止ワードが使用されています")
        return value