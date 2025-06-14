
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register("users", UserViewset, basename="users")
router.register("register", RegisterViewset, basename="register")
router.register("login", LoginViewset, basename="login")


# Register Viewsets here
urlpatterns = router.urls + []