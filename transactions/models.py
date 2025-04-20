from django.db import models

from .constants import TRANSACTION_TYPE_CHOICES
from accounts.models import UserBankAccount, CentralBankAccount

from django.core.exceptions import ValidationError


class Transaction(models.Model):
    account = models.ForeignKey(
        UserBankAccount,
        related_name='transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    central_account = models.ForeignKey(
        CentralBankAccount,
        related_name='transactions',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    balance_after_transaction = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    transaction_type = models.PositiveSmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, blank=True)  # For tracking transfers
    destination_account = models.CharField(max_length=20, blank=True)  # For interbank transfers

    def __str__(self):
        return f"{self.account or self.central_account} - {self.amount}"
    
    def clean(self):
        """Ensure at least one account is specified"""
        if not self.account and not self.central_account:
            raise ValidationError("Either account or central_account must be specified")

    class Meta:
        ordering = ['timestamp']