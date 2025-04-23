from rest_framework import serializers
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from .models import *
from accounts.models import *
from transactions.models import *
from .webhooks import WebhookService
# from .constants import GENDER_CHOICE

from datetime import datetime, timedelta
from uuid import UUID

from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from uuid import uuid4
from core.utils import hash256, generate_secure_six_digits

from django.db import transaction


phone_validator = RegexValidator(
    regex=r"^(7|9)\d{8}$",
    message="Phone number must be 8-12 digits (e.g., +251945678903).",
)

    
class Bank2BankTransactionSerializer(serializers.ModelSerializer):
    receiver_bank = serializers.CharField(write_only=True)
    destination_account = serializers.CharField(write_only=True)
    
    sender_bank = serializers.SerializerMethodField(read_only=True)
    settlement_ref = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "sender_bank", "receiver_bank", "destination_account",
            "amount", "transaction_type", "settlement_ref"
        ]

    # obj is the actual Transaction model instance being serialized.
    def get_sender_bank(self, obj):
        return obj.source_account.branch.commercial_bank.name # Who sent this one?

    # SerializerMethodField, which computes custom values for serialization.
    def get_settlement_ref(self, obj):
        return obj.nbe_settlement_ref

    def validate(self, data):
        """Validate receiver account and bank reserves"""
        user_account = self.context['request'].user.account.first() # Who is sending now?
        if not user_account:
            raise serializers.ValidationError("Sender account not found")

        amount = data['amount']
        sender_bank = user_account.branch.commercial_bank

        if sender_bank.reserve_balance < amount:
            raise serializers.ValidationError(
                {"amount": "Insufficient reserves in sender bank"}
            )

        try:
            receiver_bank = CommercialBank.objects.get(name=data['receiver_bank'])
            receiver_account = BankAccount.objects.get(
                account_number=data['destination_account'],
                branch__commercial_bank=receiver_bank
            )
        except (CommercialBank.DoesNotExist, BankAccount.DoesNotExist):
            raise serializers.ValidationError("Receiver account not found in specified bank")

        data.update({
            'sender_account': user_account,
            'receiver_account': receiver_account,
            'sender_bank': sender_bank,
            'receiver_bank': receiver_bank
        })
        return data

    @transaction.atomic # Ensure atomicity [Mat Man Sunuwawa] ... If any error occurs, all changes are rolled back (like an "undo" button).
    def create(self, validated_data):
        sender_account = validated_data['sender_account']
        receiver_account = validated_data['receiver_account']
        sender_bank = validated_data['sender_bank']
        receiver_bank = validated_data['receiver_bank']
        amount = validated_data['amount']

        timestamp = datetime.now().strftime("%H%M%S")
        ref_no = f"SETT-{timestamp}"

        # 1. Create records
        transaction_record = Transaction.objects.create(
            source_account=sender_account,
            destination_account=receiver_account,
            amount=amount,
            transaction_type="INTERBANK",
            nbe_settlement_ref=ref_no
        )

        settlement = InterbankSettlement.objects.create(
            sender_bank=sender_bank,
            receiver_bank=receiver_bank,
            amount=amount,
            status="COMPLETED",
            reference_number=ref_no
        )

        # 1. Update customer balances
        sender_account.balance -= amount
        receiver_account.balance += amount

        # 2. Update bank reserves
        sender_bank.reserve_balance -= amount
        receiver_bank.reserve_balance += amount

        # 3. Update central bank total reserves
        central_bank = sender_bank.nbe
        central_bank.total_reserves -= amount
        central_bank.total_reserves += amount

        # Single save point for atomicity
        models_to_save = [
            sender_account, receiver_account,
            sender_bank, receiver_bank,
            central_bank
        ]
        for model in models_to_save:
            model.save()
        # If anything fails here, BOTH changes are canceled.
            
        transaction.on_commit(
            lambda: WebhookService.trigger_webhook(
                receiver_account,
                {
                    "event": "transaction.received",
                    "amount": str(amount),
                    "currency": receiver_account.currency,
                    "sender_account": sender_account.account_number,
                    "sender_bank": sender_bank.name,
                    "reference": ref_no,
                    "timestamp": now().isoformat(),
                    "settlement_type": "INTERBANK"
                }
            )
        )

        return transaction_record
    
# I will Teach Myself [Matu Sunuwawa]
    # Complete Transaction Flow
    # 1. Client Makes API Request
    # 2. Serializer Validation Phase [ def validate(self, data): ]
    # 3. Creation Phase [ def create(self, validated_data): ]
    # 4.Serialization Phase (When Viewing Data) [ def get_source_account(self, obj): ]
