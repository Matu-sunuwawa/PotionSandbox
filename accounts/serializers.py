
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

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    account_type = serializers.CharField(write_only=True)
    branch_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'password',
            'account_type',
            'branch_code'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        account_type = validated_data.pop('account_type')
        branch_code = validated_data.pop('branch_code')
        
        user = User.objects.create(
            **validated_data,
            is_phone_verified=True,
            is_email_verified=True,
            is_active=True
        )
        user.set_password(password)
        user.save()

        # Get branch
        branch = Branch.objects.get(branch_code=branch_code)
        
        account_no = f"{settings.ACCOUNT_NUMBER_START_FROM}{datetime.now().strftime('%H%M%S')}"
        BankAccount.objects.create(
            owner=user,
            branch=branch,
            account_type=account_type,
            account_number=account_no
        )

        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'id': instance.id,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'phone_number': instance.phone_number
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


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

