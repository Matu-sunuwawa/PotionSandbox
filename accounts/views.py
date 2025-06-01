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

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import *
from .serializers import *

from transactions.models import *
from transactions.constants import *


class LoginViewset(GenericViewSet, CreateModelMixin):
    serializer_class = UserLoginSerializer

class RegisterViewset(GenericViewSet, CreateModelMixin):
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    permission_classes = []



class UserViewset(GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        user = request.user
        serializer = UserBalanceSerializer(user)
        return Response(serializer.data)




