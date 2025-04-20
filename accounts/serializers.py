
from rest_framework import serializers
from django.conf import settings
from django.db import transaction

from .models import *
from .constants import GENDER_CHOICE

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

from .dispatch import *
from .dispatch import user_phone_verified

phone_validator = RegexValidator(
    regex=r"^(7|9)\d{8}$",
    message="Phone number must be 8-12 digits (e.g., +251945678903).",
)

class UserGeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "is_phone_verified",
            "is_email_verified",
            "date_joined",
        ]

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            'street_address',
            'city',
            'postal_code',
            'country'
        ]

class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    account_type = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICE, write_only=True)
    birth_date = serializers.DateField(write_only=True)
    address = UserAddressSerializer(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'password1',
            'password2',
            'account_type', # This is the string name from request
            'gender',
            'birth_date',
            'address'
        ]
        extra_kwargs = {
            'password1': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    @transaction.atomic
    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        account_type_name = validated_data.pop('account_type') # Get the string name
        gender = validated_data.pop('gender')
        birth_date = validated_data.pop('birth_date')
        password = validated_data.pop('password1')
        validated_data.pop('password2', None)  # Remove password2 as we don't need it anymore

        bank_account_type = BankAccountType.objects.get(name=account_type_name)

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        timestamp = datetime.now().strftime("%H%M%S")
        account_no = f"{settings.ACCOUNT_NUMBER_START_FROM}{timestamp}"

        UserBankAccount.objects.create(
            user=user,
            gender=gender,
            birth_date=birth_date,
            account_type=bank_account_type, # Use the instance here
            account_no=account_no
        )

        if address_data:
            UserAddress.objects.create(user=user, **address_data)

        user_registered.send(User, **{"instance": user, "method": "PHONE"})

        return user

    def to_representation(self, instance):
        # Return only basic User info in response
        return {
            'id': instance.id,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'phone_number': instance.phone_number
        }


class CreateVerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    user_id = serializers.UUIDField(write_only=True)
    code_type = serializers.ChoiceField([(1, "PHONE"), (2, "EMAIL")], write_only=True)

    detail = serializers.SerializerMethodField()
    user = UserGeneralInfoSerializer(read_only=True)

    def get_detail(self, instance):
        return "Success"

    def create(self, validated_data):
        code = validated_data.get("code")
        code_type = validated_data.get("code_type")
        user_id = validated_data.get("user_id")

        queryset = VerificationCode.objects.filter(
            user__id=user_id, code_type=code_type, is_used=False
        )

        instance = get_object_or_404(queryset, token=hash256(code))

        if code_type == 1:
            instance.user.is_phone_verified = True
        else:
            instance.user.is_email_verified = True
        instance.is_used = True
        instance.user.save()
        instance.save()

        user_phone_verified.send(User, **{"instance": instance.user})

        return instance
    

class ResendVerificationSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )
    code_type = serializers.ChoiceField(choices=[(1, "PHONE"), (2, "EMAIL")])
    detail = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        code_type = validated_data.pop("code_type")
        token = generate_secure_six_digits()
        VerificationCode.objects.create(
            expires_at=datetime.now() + timedelta(minutes=5),
            token=token,
            code_type=code_type,
            user=user_id,
        )
        TemporaryCode.objects.create(code=token, phone_number=user_id.phone_number)

        return {"user_id": user_id, "code_type": code_type, "detail": "success"}


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    user = UserGeneralInfoSerializer(read_only=True)

    def validate(self, attrs):
        password = attrs.pop("password")
        phone_number = attrs.pop("phone_number")

        phone_number = User.normalize_phone_number(phone_number)

        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise ValidationError(
                {
                    "phone_number": "No user found with the given credentials",
                    "password": "no user found with the given credentials",
                }
            )

        attrs = super().validate(attrs)

        attrs["user"] = user

        return attrs

    def create(self, validated_data):
        user = validated_data.pop("user")
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user,
        }
    

class CentralBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentralBankAccount
        fields = ['id', 'name', 'account_no', 'balance']
        read_only_fields = ['id', 'name', 'account_no', 'balance']


# class InterbankTransferSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InterbankTransfer
#         fields = ['sender_account', 'receiver_account', 'amount', 'reference']
#         extra_kwargs = {
#             'sender_account': {'read_only': True}
#         }

#     def validate_receiver_account(self, value):
#         """Validate the receiving account exists"""
#         if not UserBankAccount.objects.filter(account_no=value).exists():
#             raise serializers.ValidationError("Receiver account not found")
#         return value

#     def validate_amount(self, value):
#         if value <= 0:
#             raise serializers.ValidationError("Amount must be positive")
#         return value


class UserTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterbankTransfer
        fields = ['receiver_account', 'amount', 'reference']
        
    def validate_receiver_account(self, value):
        if self.context['request'].user.is_superuser:
            raise serializers.ValidationError("Superuser action not allowed.")
        if not UserBankAccount.objects.filter(account_no=value).exists():
            raise serializers.ValidationError("Receiver account not found")
        if value == self.context['request'].user.account.account_no:
            raise serializers.ValidationError("Cannot transfer to yourself")
        return value

class CentralBankTransferDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterbankTransfer
        fields = ['receiver_account', 'amount', 'reference']

    def validate_receiver_account(self, value):
        """Validate the receiving account exists"""
        if not UserBankAccount.objects.filter(account_no=value).exists():
            raise serializers.ValidationError("The User Account is not found")
        return value

    def validate(self, data):
        """Validate amount against account limits"""
        amount = data['amount']
        min_deposit = settings.MINIMUM_DEPOSIT_AMOUNT

        if amount < min_deposit:
            raise serializers.ValidationError({
                'amount': f'You can withdraw at least {min_deposit} $'
            })

        return data


class CentralBankTransferWithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterbankTransfer
        fields = ['receiver_account', 'amount', 'reference']


    def validate_receiver_account(self, value):
        """Validate the receiving account exists"""
        if not UserBankAccount.objects.filter(account_no=value).exists():
            raise serializers.ValidationError("The User Account is not found")
        return value

    def validate(self, data):
        """Validate amount against account limits"""
        user_account = UserBankAccount.objects.get(account_no=data['receiver_account'])
        amount = data['amount']
        min_withdraw = settings.MINIMUM_WITHDRAWAL_AMOUNT
        max_withdraw = user_account.account_type.maximum_withdrawal_amount

        if amount < min_withdraw:
            raise serializers.ValidationError({
                'amount': f'You can withdraw at least {min_withdraw} $'
            })

        if amount > max_withdraw:
            raise serializers.ValidationError({
                'amount': f'You can withdraw at most {max_withdraw} $'
            })

        if amount > user_account.balance:
            raise serializers.ValidationError({
                'amount': f'You have {user_account.balance} $ in your account. '
                          'You cannot withdraw more than your account balance'
            })

        return data