from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """拡張ユーザーモデル"""
    nickname = models.CharField(max_length=50, blank=True)
    class Meta:
        verbose_name_plural = "CustomUser"
