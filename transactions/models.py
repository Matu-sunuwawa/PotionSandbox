from django.db import models

from accounts.models import *
from banks.models import *
from .constants import *

class Transaction(models.Model):
    source_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='sent_transactions',null=True,blank=True,)
    destination_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='received_transactions',null=True,blank=True,)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    remarks = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    nbe_settlement_ref = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class InterbankSettlement(models.Model):
    sender_bank = models.ForeignKey(CommercialBank, on_delete=models.CASCADE, related_name='sent_settlements')
    receiver_bank = models.ForeignKey(CommercialBank, on_delete=models.CASCADE, related_name='received_settlements')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    settlement_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_TYPES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Settlement {self.reference_number} - {self.amount}"