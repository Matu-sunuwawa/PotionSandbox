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
from rest_framework.pagination import PageNumberPagination

from transactions.models import *
from transactions.serializers import *
from transactions.constants import *


class User2UserViewset(GenericViewSet, CreateModelMixin):
    serializer_class = IntraBankTransferSerializer
    permission_classes = [IsAuthenticated]


class TransactionViewset(GenericViewSet, ListModelMixin):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        user_account = user.account.first()
        if not user_account:
            return Transaction.objects.none()

        # Get all valid transactions where user is either sender or receiver
        return Transaction.objects.filter(
            (models.Q(source_account=user_account)) | 
            (models.Q(destination_account=user_account)),
            models.Q(source_account__isnull=False) | 
            models.Q(destination_account__isnull=False)
        ).select_related(
            'source_account',
            'destination_account',
            'source_account__owner',
            'destination_account__owner'
        ).order_by('-timestamp')


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