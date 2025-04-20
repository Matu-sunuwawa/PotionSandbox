from rest_framework import serializers
from django.conf import settings
from datetime import datetime
from transactions.models import Transaction
from accounts.models import UserBankAccount

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'timestamp', 'balance_after_transaction']
        read_only_fields = ['timestamp', 'balance_after_transaction']

# class DepositSerializer(TransactionSerializer):
#     def validate_amount(self, value):
#         min_deposit = settings.MINIMUM_DEPOSIT_AMOUNT
#         if value < min_deposit:
#             raise serializers.ValidationError(
#                 f'You need to deposit at least {min_deposit} $'
#             )
#         print("Value:", value)
#         return value

# class WithdrawSerializer(TransactionSerializer):
#     def validate_amount(self, value):
#         account = self.context['account']
#         min_withdraw = settings.MINIMUM_WITHDRAWAL_AMOUNT
#         max_withdraw = account.account_type.maximum_withdrawal_amount
#         balance = account.balance

#         if value < min_withdraw:
#             raise serializers.ValidationError(
#                 f'You can withdraw at least {min_withdraw} $'
#             )
#         if value > max_withdraw:
#             raise serializers.ValidationError(
#                 f'You can withdraw at most {max_withdraw} $'
#             )
#         if value > balance:
#             raise serializers.ValidationError(
#                 f'You have {balance} $ in your account. '
#                 'You cannot withdraw more than your account balance'
#             )
#         return value

class DateRangeSerializer(serializers.Serializer):
    daterange = serializers.CharField(required=False)

    def validate_daterange(self, value):
        try:
            dates = value.split(' - ')
            if len(dates) == 2:
                for date in dates:
                    datetime.strptime(date, '%Y-%m-%d')
                return dates
            raise serializers.ValidationError("Please select a date range.")
        except (ValueError, AttributeError):
            raise serializers.ValidationError("Invalid date range")