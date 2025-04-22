
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register("bank2bank/transfer", Bank2BankViewset, basename="bank-to-bank")

# Register Viewsets here
urlpatterns = router.urls + []