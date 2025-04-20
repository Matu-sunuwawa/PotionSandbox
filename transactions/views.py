from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.conf import settings

from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from transactions.models import Transaction
from transactions.serializers import (
    # DepositSerializer,
    # WithdrawSerializer,
    DateRangeSerializer,
    TransactionSerializer
)
from transactions.constants import DEPOSIT, WITHDRAWAL

class TransactionListViewset(GenericViewSet, CreateModelMixin, ListModelMixin):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            account=self.request.user.account
        )
        
        date_serializer = DateRangeSerializer(data=self.request.query_params)
        if date_serializer.is_valid() and date_serializer.validated_data.get('daterange'):
            date_range = date_serializer.validated_data['daterange']
            queryset = queryset.filter(timestamp__date__range=date_range)
            
        return queryset

# class DepositViewset(GenericViewSet, CreateModelMixin):
#     serializer_class = DepositSerializer
#     permission_classes = [IsAuthenticated]

#     def get_serializer_context(self):
#         """Add the user's account to the serializer context."""
#         context = super().get_serializer_context()
#         context['account'] = self.request.user.account
#         return context

#     def perform_create(self, serializer):
#         account = self.request.user.account # look at me 😊
#         central_account = self.request.user.central_account
#         amount = serializer.validated_data['amount']
        
#         # Handle initial deposit date and interest calculation
#         if not account.initial_deposit_date:
#             now = timezone.now()
#             next_interest_month = int(
#                 12 / account.account_type.interest_calculation_per_year
#             )
#             account.initial_deposit_date = now
#             account.interest_start_date = (
#                 now + relativedelta(months=+next_interest_month)
#             )

#         # Update account balance
#         account.balance += amount
#         account.save(update_fields=[
#             'initial_deposit_date',
#             'balance',
#             'interest_start_date'
#         ])

#         # Create transaction record
#         serializer.save(
#             account=account,
#             central_account=central_account,
#             transaction_type=DEPOSIT,
#             balance_after_transaction=account.balance
#         )

# class WithdrawViewset(GenericViewSet, CreateModelMixin):
#     serializer_class = WithdrawSerializer
#     permission_classes = [IsAuthenticated]

#     def get_serializer_context(self):
#         """Add the user's account to the serializer context."""
#         context = super().get_serializer_context()
#         context['account'] = self.request.user.account
#         return context

#     def perform_create(self, serializer):
#         account = self.request.user.account
#         amount = serializer.validated_data['amount']

#         # Update account balance
#         account.balance -= amount
#         account.save(update_fields=['balance'])

#         # Create transaction record
#         serializer.save(
#             account=account,
#             transaction_type=WITHDRAWAL,
#             balance_after_transaction=account.balance
#         )
