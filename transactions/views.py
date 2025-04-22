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

from transactions.models import *
from transactions.serializers import *
from transactions.constants import *


class User2UserViewset(GenericViewSet, CreateModelMixin):
    serializer_class = IntraBankTransferSerializer
    permission_classes = [IsAuthenticated]
