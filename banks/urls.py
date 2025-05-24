
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register("bank2mela/transfer", Bank2BankViewset, basename="bank-to-bank")
router.register(r"receive/external", ReceiveMoneyExternalViewset, basename="receive-external")

# Register Viewsets here
urlpatterns = router.urls + []