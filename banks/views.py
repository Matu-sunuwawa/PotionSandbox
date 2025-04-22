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


class Bank2BankViewset(GenericViewSet, CreateModelMixin):
    serializer_class = Bank2BankTransactionSerializer
    permission_classes = [IsAuthenticated]
    queryset = InterbankSettlement.objects.all()