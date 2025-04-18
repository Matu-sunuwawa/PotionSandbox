
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register("transactions", TransactionListViewset, basename="transactions")
router.register("deposit", DepositViewset, basename="deposit")
router.register("withdraw", WithdrawViewset, basename="withdraw")

# Register Viewsets here
urlpatterns = router.urls + []