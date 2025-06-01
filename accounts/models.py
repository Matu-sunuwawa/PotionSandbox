
import re
from uuid import uuid4
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    EmailValidator,
    FileExtensionValidator,
    RegexValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from .constants import GENDER_CHOICE, ACCOUNT_TYPES
from .managers import UserManager

from core.utils import hash256

from banks.models import *

phone_regex = r"^(\+)?(?P<country_code>251)?(?P<phone_number>[79]\d{8})$"
phone_validator = RegexValidator(
    regex=phone_regex,
    message="Phone number must start with +2519, 2519, 9, +2517, 2517, or 7 followed by 8 digits.",
)


class User(AbstractUser):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    profile_pic_id = models.UUIDField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=255,
        unique=True,
        validators=[phone_validator],
    )
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)

    user_type = models.CharField(
        max_length=255, choices=(("user", "user"), ("busines", "bussines"))
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name"]

    objects = UserManager()


    @property
    def balance(self):
        account = self.account.first()  # Get the first associated account
        if account:
            return account.balance
        return 0
    
    @staticmethod
    def normalize_phone_number(phone_number):
        match = re.search(phone_regex, phone_number)

        if not match:
            raise ValueError("Invalid phone number value")

        return match.groupdict()["phone_number"]

    def __str__(self):
        return self.phone_number

    def save(self, **kwrags):
        self.phone_number = User.normalize_phone_number(self.phone_number)

        return super().save(**kwrags)

class BankAccount(models.Model):
    account_number = models.PositiveIntegerField(unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='ETB')
    opened_date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name='account', on_delete=models.CASCADE)
    webhook_url = models.URLField(
        blank=True,
        null=True,
        help_text="Endpoint to notify about incoming transactions"
    )

    def __str__(self):
        return f"{self.account_number} - {self.owner.get_full_name()}"