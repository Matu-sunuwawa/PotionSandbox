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


class WebhookTestViewset(GenericViewSet, CreateModelMixin):
    """Sandbox webhook receiver for testing"""
    def create(self, request, *args, **kwargs):
        print("\n=== WEBHOOK RECEIVED ===")
        print("Headers:", request.headers)
        print("Body:", request.data)
        print("=======================\n")
        
        return Response(
            {"status": "received", "data": request.data},
            status=status.HTTP_200_OK
        )