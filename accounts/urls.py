
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register("register", RegisterViewset, basename="register")
router.register(
    "verifications/confirm", VerificationCodeViewset, basename="users-confirm-code"
)
router.register(
    "verifications/resend", VerificationCodeResendViewset, basename="users-resend-code"
)
router.register("login", LoginViewset, basename="login")

router.register("central-bank/detail", CentralBankAccountViewset, basename="central-bank")
router.register("central-bank/deposit", CentralBankTransferDepositViewset, basename="central-bank-deposit") # Deposite Done by Accountant|SuperUser
router.register("central-bank/withdraw", CentralBankTransferWithdrawViewset, basename="central-bank-withdraw") # Deposite Done by Accountant|SuperUser
router.register("user/transfer", UserTransferViewset, basename="users-interbank-transfer")

# Register Viewsets here
urlpatterns = router.urls + []