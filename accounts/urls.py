
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


# Register Viewsets here
urlpatterns = router.urls + []