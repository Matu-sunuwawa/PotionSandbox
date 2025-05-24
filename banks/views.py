
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

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from banks.permissions import ExternalSysPermission
from banks.serializers import ReceiveMoneyExternalSerializer


class Bank2BankViewset(GenericViewSet, CreateModelMixin):
    serializer_class = Bank2BankTransactionSerializer
    queryset = InterbankSettlement.objects.all()
    permission_classes = [IsAuthenticated]


class ReceiveMoneyExternalViewset(CreateModelMixin, GenericViewSet):
    serializer_class = ReceiveMoneyExternalSerializer
    permission_classes = [ExternalSysPermission]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="X-Access-Id",
                type=OpenApiTypes.STR,
                required=True,
                location=OpenApiParameter.HEADER,
            ),
            OpenApiParameter(
                name="X-Access-Secret",
                type=OpenApiTypes.STR,
                required=True,
                location=OpenApiParameter.HEADER,
            ),
        ],
        request=ReceiveMoneyExternalSerializer,
        responses={201: ReceiveMoneyExternalSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

