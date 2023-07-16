from __future__ import annotations

from typing import Union, Optional, Tuple

from django.db import models
from django.db.models import QuerySet, Manager
from telegram import Update
from telegram.ext import CallbackContext

from tgbot.utils.info import extract_user_data_from_update
from utils.models import CreateUpdateTracker, GetOrNoneManager


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=32, unique=True)  # telegram user_id
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    language_code = models.CharField(max_length=8, null=True, blank=True, default="ru")
    deep_link = models.CharField(max_length=64, null=True, blank=True)
    is_blocked_bot = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)
    is_first_time = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.username:
            return self.username
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        return str(self.user_id)

    @classmethod
    def get_user(cls, update: Update) -> User:
        try:
            data = extract_user_data_from_update(update)
            return cls.objects.get(user_id=data["user_id"])
        except cls.DoesNotExist:
            return False

    @property
    def tg_str(self) -> str:
        if self.username:
            return f"@{self.username}"
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"

    @property
    def short_tg_str(self) -> str:
        if self.username:
            return self.username
        return self.user_id
