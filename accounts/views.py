from datetime import datetime

from django.shortcuts import get_object_or_404, render

from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import *
from .serializers import *


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