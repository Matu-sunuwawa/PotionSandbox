from rest_framework import serializers
from django.conf import settings
from django.db import transaction

from .models import *
from accounts.models import *
from transactions.models import *
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
        """Validate receiver account exists in the specified bank"""
        user_account = self.context['request'].user.account.first() # Who is sending now?
        if not user_account:
            raise serializers.ValidationError("Sender account not found")

        try:
            receiver_bank = CommercialBank.objects.get(name=data['receiver_bank'])
            receiver_account = BankAccount.objects.get(
                account_number=data['destination_account'],
                branch__commercial_bank=receiver_bank
            )
        except (CommercialBank.DoesNotExist, BankAccount.DoesNotExist):
            raise serializers.ValidationError("Receiver account not found in specified bank")

        data['sender_account'] = user_account
        data['receiver_account'] = receiver_account
        return data

    @transaction.atomic # Ensure atomicity [Mat Man Sunuwawa] ... If any error occurs, all changes are rolled back (like an "undo" button).
    def create(self, validated_data):
        sender_account = validated_data['sender_account']
        receiver_account = validated_data['receiver_account']
        amount = validated_data['amount']
        receiver_bank_name = validated_data.pop('receiver_bank')

        timestamp = datetime.now().strftime("%H%M%S")
        ref_no = f"SETT-{timestamp}"

        transaction_record = Transaction.objects.create(
            source_account=sender_account,
            destination_account=receiver_account,
            amount=amount,
            transaction_type="INTERBANK",
            nbe_settlement_ref=ref_no
        )

        settlement = InterbankSettlement.objects.create(
            sender_bank=sender_account.branch.commercial_bank,
            receiver_bank=receiver_account.branch.commercial_bank,
            amount=amount,
            status="COMPLETED",
            reference_number=ref_no
        )

        sender_account.balance -= amount
        receiver_account.balance += amount
        sender_account.save()
        receiver_account.save()
        # If anything fails here, BOTH changes are canceled.

        return transaction_record
    
# I will Teach Myself [Matu Sunuwawa]
    # Complete Transaction Flow
    # 1. Client Makes API Request
    # 2. Serializer Validation Phase [ def validate(self, data): ]
    # 3. Creation Phase [ def create(self, validated_data): ]
    # 4.Serialization Phase (When Viewing Data) [ def get_source_account(self, obj): ]
