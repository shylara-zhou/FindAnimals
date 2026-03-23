from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    openid = models.CharField(max_length=64, unique=True, null=True, blank=True)
    avatar_url = models.URLField(max_length=512, null=True, blank=True)
    nickname = models.CharField(max_length=64, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

