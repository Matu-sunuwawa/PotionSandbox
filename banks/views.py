
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet

from .models import *
from .serializers import *

from transactions.models import *
from transactions.constants import *


class Bank2BankViewset(GenericViewSet, CreateModelMixin):
    serializer_class = Bank2BankTransactionSerializer
    permission_classes = [IsAuthenticated]
    queryset = InterbankSettlement.objects.all()