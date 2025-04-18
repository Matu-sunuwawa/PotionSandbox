from django.apps import AppConfig
from .dispatch import *


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    label = "accounts"

    def ready(self):
        from . import signals
