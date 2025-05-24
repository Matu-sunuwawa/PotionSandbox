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
from rest_framework_simplejwt.authentication import JWTAuthentication

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
