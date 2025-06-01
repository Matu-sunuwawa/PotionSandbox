from rest_framework import serializers
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from .models import *
from accounts.models import *
from transactions.models import *
from banks.webhooks import WebhookService
# from .constants import GENDER_CHOICE

from datetime import datetime, timedelta
from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers, validators

from django.db import transaction  # Add this import


class IntraBankTransferSerializer(serializers.ModelSerializer):
    destination_account = serializers.CharField(write_only=True)
    
    source_account = serializers.SerializerMethodField(read_only=True)
    destination_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "source_account",
            "destination_account",
            "destination_details",
            "amount",
            "transaction_type"
        ]
        read_only_fields = ["source_account", "destination_details"]

    def get_source_account(self, obj):
        """Current user's account number"""
        return obj.source_account.account_number

    def get_destination_details(self, obj):
        """Structured recipient info"""
        account = obj.destination_account
        return {
            "account_number": account.account_number,
            "owner": account.owner.get_full_name(),
            "branch": account.branch.branch_code
        }

    def validate(self, data):
        """Validate same-bank transfer conditions"""
        source_account = self.context['request'].user.account.first()
        if not source_account:
            raise serializers.ValidationError("Sender account not found")

        try:
            recipient = BankAccount.objects.get(
                account_number=data['destination_account'],
                branch__commercial_bank=source_account.branch.commercial_bank
            )
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError({
                "destination_account": "Account not found in your bank"
            })

        if source_account.balance < data['amount']:
            raise serializers.ValidationError(
                {"amount": "Insufficient funds"}
            )

        data['source_account'] = source_account
        data['destination_account_instance'] = recipient
        return data

    @transaction.atomic # my beloved logic here
    def create(self, validated_data):
        """Execute the transfer atomically"""
        source = validated_data['source_account']
        destination = validated_data['destination_account_instance']
        amount = validated_data['amount']

        source.balance -= amount
        destination.balance += amount
        source.save()
        destination.save()

        transaction.on_commit(
            lambda: WebhookService.trigger_webhook(
                destination,
                {
                    "event": "transaction.received",
                    "amount": str(amount),
                    "currency": source.currency,
                    "sender_account": source.account_number,
                    "timestamp": now().isoformat(),
                    "settlement_type": "INTRABANK"
                }
            )
        )

        return Transaction.objects.create(
            source_account=source,
            destination_account=destination,
            amount=amount,
            transaction_type="INTRABANK",
            nbe_settlement_ref=f"INTRA-{datetime.now().strftime('%H%M%S')}"
        )


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    other_party = serializers.SerializerMethodField()
    direction = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'amount',
            'transaction_type',
            'transaction_type_display',
            'remarks',
            'timestamp',
            'other_party',
            'direction',
            'status'
        ]

    def get_other_party(self, obj):
        request = self.context.get('request')
        if not request:
            return None
            
        user_account = request.user.account.first()
        if not user_account:
            return None

        if obj.source_account == user_account:
            # Outgoing transaction
            if obj.destination_account:
                return {
                    'account_number': obj.destination_account.account_number,
                    'name': obj.destination_account.owner.get_full_name() if obj.destination_account.owner else 'Unknown'
                }
            return {
                'account_number': None,
                'name': 'External Account'
            }
        else:
            # Incoming transaction
            if obj.source_account:
                return {
                    'account_number': obj.source_account.account_number,
                    'name': obj.source_account.owner.get_full_name() if obj.source_account.owner else 'Unknown'
                }
            return {
                'account_number': None,
                'name': 'External Account'
            }

    def get_direction(self, obj):
        request = self.context.get('request')
        if not request:
            return None
            
        user_account = request.user.account.first()
        if not user_account:
            return None

        return 'outgoing' if obj.source_account == user_account else 'incoming'

    def get_status(self, obj):
        return 'completed'  # You can add more sophisticated status logic here


# I will Teach Myself [Matu Sunuwawa]
    # Complete Transaction Flow
    # 1. Client Makes API Request
    # 2. Serializer Validation Phase [ def validate(self, data): ]
    # 3. Creation Phase [ def create(self, validated_data): ]
    # 4.Serialization Phase (When Viewing Data) [ def get_source_account(self, obj): ]