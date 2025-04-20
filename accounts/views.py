from datetime import datetime

from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import *
from .serializers import *

from transactions.models import *
from transactions.constants import *


class LoginViewset(GenericViewSet, CreateModelMixin):
    serializer_class = UserLoginSerializer

class RegisterViewset(GenericViewSet, CreateModelMixin):
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    permission_classes = []

class VerificationCodeViewset(CreateModelMixin, GenericViewSet):
    serializer_class = CreateVerificationCodeSerializer

class VerificationCodeResendViewset(CreateModelMixin, GenericViewSet):
    serializer_class = ResendVerificationSerializer


class CentralBankAccountViewset(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    serializer_class = CentralBankAccountSerializer
    permission_classes = [IsAuthenticated]
    queryset = CentralBankAccount.objects.all()
    
    def get_object(self):
        return CentralBankAccount.get_main_account()
    
    def list(self, request, *args, **kwargs):
        """Override list to only show the main account"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserTransferViewset(GenericViewSet, CreateModelMixin):
    serializer_class = UserTransferSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        data = serializer.validated_data
        sender = self.request.user.account
        
        with transaction.atomic():
            recipient = UserBankAccount.objects.select_for_update().get(
                account_no=data['receiver_account']
            )
            
            if sender.balance < data['amount']:
                raise serializers.ValidationError(
                    {"error": "Insufficient funds"}
                )
            
            # Perform transfer
            sender.balance -= data['amount']
            recipient.balance += data['amount']
            
            sender.save()
            recipient.save()
            
            # Record transactions
            Transaction.objects.bulk_create([
                Transaction(
                    account=sender,
                    amount=data['amount'],
                    balance_after_transaction=sender.balance,
                    transaction_type=WITHDRAWAL,
                    destination_account=recipient.account_no
                ),
                Transaction(
                    account=recipient,
                    amount=data['amount'],
                    balance_after_transaction=recipient.balance,
                    transaction_type=DEPOSIT,
                    reference=data.get('reference', '')
                )
            ])
            
            serializer.save(
                sender_account=sender.account_no,
                status='COMPLETED',
                completed_at=datetime.now()
            )

class CentralBankTransferDepositViewset(GenericViewSet, CreateModelMixin):
    serializer_class = CentralBankTransferDepositSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        data = serializer.validated_data
        central_account = CentralBankAccount.get_main_account()
        
        with transaction.atomic():
            recipient = UserBankAccount.objects.select_for_update().get(
                account_no=data['receiver_account']
            )

            # Handle initial deposit and interest calculation
            if not recipient.initial_deposit_date:
                now = timezone.now()
                next_interest_month = int(
                    12 / recipient.account_type.interest_calculation_per_year
                )
                recipient.initial_deposit_date = now
                recipient.interest_start_date = now + relativedelta(months=+next_interest_month)
            
            # Add money to system
            central_account.balance += data['amount']
            recipient.balance += data['amount']
            
            central_account.save()
            recipient.save()


            # Record transactions - now properly setting central_account
            Transaction.objects.bulk_create([
                Transaction(
                    central_account=central_account,
                    amount=data['amount'],
                    balance_after_transaction=central_account.balance,
                    transaction_type=DEPOSIT,
                    reference="Central Bank Disbursement"
                ),
                Transaction(
                    account=recipient,
                    amount=data['amount'],
                    balance_after_transaction=recipient.balance,
                    transaction_type=DEPOSIT,
                    reference=data.get('reference', '')
                )
            ])
            
            serializer.save(
                sender_account=central_account.account_no,
                status='COMPLETED',
                completed_at=datetime.now()
            )


class CentralBankTransferWithdrawViewset(GenericViewSet, CreateModelMixin):
    serializer_class = CentralBankTransferWithdrawSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        data = serializer.validated_data
        central_account = CentralBankAccount.get_main_account()
        
        with transaction.atomic():
            recipient = UserBankAccount.objects.select_for_update().get(
                account_no=data['receiver_account']
            )
            
            # Subtract money from system
            central_account.balance -= data['amount']
            recipient.balance -= data['amount']
            
            central_account.save()
            recipient.save()
            
            # Record transactions - now properly setting central_account
            Transaction.objects.bulk_create([
                Transaction(
                    central_account=central_account,
                    amount=data['amount'],
                    balance_after_transaction=central_account.balance,
                    transaction_type=WITHDRAWAL,
                    reference="Central Bank Withdrawal"
                ),
                Transaction(
                    account=recipient,
                    amount=data['amount'],
                    balance_after_transaction=recipient.balance,
                    transaction_type=WITHDRAWAL,
                    reference=data.get('reference', '')
                )
            ])
            
            serializer.save(
                sender_account=central_account.account_no,
                status='COMPLETED',
                completed_at=datetime.now()
            )
