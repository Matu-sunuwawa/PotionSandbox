
from datetime import datetime
import requests
from rest_framework import serializers
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from .models import *
from accounts.models import *
from transactions.models import *
from .webhooks import WebhookService
# from .constants import GENDER_CHOICE


from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from uuid import uuid4
from core.utils import hash256, generate_secure_six_digits

from django.db import transaction

from rest_framework import serializers
from accounts.models import User, BankAccount
from transactions.models import Transaction

import logging

# Configure the logger
logging.basicConfig(level=logging.ERROR)

# Get a logger instance
logger = logging.getLogger(__name__)



phone_validator = RegexValidator(
    regex=r"^(7|9)\d{8}$",
    message="Phone number must be 8-12 digits (e.g., +251945678903).",
)

    
class Bank2BankTransactionSerializer(serializers.ModelSerializer):
    receiver_bank = serializers.CharField(write_only=True)
    destination_phone_number = serializers.CharField(write_only=True)
    remarks = serializers.CharField(write_only=True, required=False)
    
    sender_bank = serializers.SerializerMethodField(read_only=True)
    settlement_ref = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "sender_bank", "receiver_bank", "destination_phone_number",
            "remarks", "amount", "transaction_type", "settlement_ref"
        ]

    def get_sender_bank(self, obj):
        return obj.source_account.branch.commercial_bank.name

    def get_settlement_ref(self, obj):
        return obj.nbe_settlement_ref

    def validate(self, data):
        user = self.context['request'].user
        amount = data['amount']

        user_account = user.account.first()
        if not user_account:
            raise serializers.ValidationError("Sender account not found")

        sender_bank = user_account.branch.commercial_bank
        if sender_bank.reserve_balance < amount:
            raise serializers.ValidationError(
                {"amount": "Insufficient reserves in sender bank"}
            )
        sender_account = user_account

        try:
            mela_wallet_bank = CommercialBank.objects.get(name="Mela Wallet")
            
            receiver_account = BankAccount.objects.get(
                owner__phone_number=data['destination_phone_number'],
                branch__commercial_bank=mela_wallet_bank
            )
        except CommercialBank.DoesNotExist:
            raise serializers.ValidationError({"receiver_bank": "Mela Wallet bank not found"})
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError({"destination_phone_number": "Receiver account not found in Mela Wallet"})

        data.update({
            'sender_account': sender_account,
            'sender_bank': sender_bank,
            'receiver_account': receiver_account,
            'receiver_bank': mela_wallet_bank
        })
        return data

    @transaction.atomic
    def create(self, validated_data):
        sender_account = validated_data['sender_account']
        receiver_account = validated_data['receiver_account']
        sender_bank = validated_data['sender_bank']
        receiver_bank = validated_data['receiver_bank']
        amount = validated_data['amount']
        remarks = validated_data.get('remarks', '')

        timestamp = datetime.now().strftime("%H%M%S")
        ref_no = f"SETT-{timestamp}"

        transaction_record = Transaction.objects.create(
            source_account=sender_account,
            destination_account=receiver_account,
            amount=amount,
            transaction_type="INTERBANK",
            nbe_settlement_ref=ref_no
        )

        InterbankSettlement.objects.create(
            sender_bank=sender_bank,
            receiver_bank=receiver_bank,
            amount=amount,
            status="COMPLETED",
            reference_number=ref_no
        )

        sender_account.balance -= amount
        receiver_account.balance += amount

        sender_bank.reserve_balance -= amount
        receiver_bank.reserve_balance += amount

        models_to_save = [sender_account, receiver_account, sender_bank, receiver_bank]
        for model in models_to_save:
            model.save()

        self.notify_external_system(
            sender_bank,
            receiver_account.owner.phone_number,
            amount,
            remarks
        )

        return transaction_record

    def notify_external_system(self, sender_bank, phone_number, amount, remarks):
        """Send notification to external system's webhook"""
        try:
            amount_float = float(amount)
            
            payload = {
                'phone_number': str(phone_number),
                'amount': amount_float,
                'remarks': str(remarks) if remarks else ""
            }
            
            access_id = getattr(sender_bank.access_key, 'access_id', 'mnbvcxz')
            access_secret = getattr(sender_bank.access_key, 'get_raw_secret', lambda: 'mnbvcxz')()
            
            response = requests.post(
                "https://potion.dev.gumisofts.com/wallets/receive/external/",
                headers={
                    'X-Access-Id': access_id,
                    'X-Access-Secret': access_secret,
                    'Content-Type': 'application/json',
                    'X-CSRFTOKEN': 'TgYWft1qUwCb3Oy6WYalyVgX9aPCr8Oj8LiiGyIjOkKYV5XsDPWwqEFuXxFGOnt7'
                },
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Notification sent successfully to {phone_number}")
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {str(e)}")
        except Exception as e:
            logger.error(f"External notification failed: {str(e)}")
        


class ReceiveMoneyExternalSerializer(serializers.Serializer):
    receiver_bank = serializers.CharField(write_only=True)
    destination_account = serializers.CharField(write_only=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('10.00'))
    remarks = serializers.CharField(required=False)
    transaction_type = serializers.CharField(default="INTERBANK", read_only=True)
    
    def validate(self, attrs):
        try:
            receiver_bank = CommercialBank.objects.get(name=attrs['receiver_bank'])
            receiver_account = BankAccount.objects.get(
                account_number=attrs['destination_account'],
                branch__commercial_bank=receiver_bank
            )
        except CommercialBank.DoesNotExist:
            raise serializers.ValidationError({"receiver_bank": "Bank not found"})
        except BankAccount.DoesNotExist:
            raise serializers.ValidationError({"destination_account": "Account not found in specified bank"})
            
        attrs['receiver_account'] = receiver_account
        return attrs

    def create(self, validated_data):
        receiver_account = validated_data['receiver_account']
        amount = validated_data['amount']
        
        transaction = Transaction.objects.create(
            destination_account=receiver_account,
            amount=amount,
            transaction_type="INTERBANK",
            remarks=validated_data.get('remarks', '')
        )
        
        receiver_account.balance += amount
        receiver_account.save()
        
        return transaction


    
# I will Teach Myself [Matu Sunuwawa]
    # Complete Transaction Flow
    # 1. Client Makes API Request
    # 2. Serializer Validation Phase [ def validate(self, data): ]
    # 3. Creation Phase [ def create(self, validated_data): ]
    # 4.Serialization Phase (When Viewing Data) [ def get_source_account(self, obj): ]
