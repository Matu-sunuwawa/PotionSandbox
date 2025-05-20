
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register("user2user/transfer", User2UserViewset, basename="user-to-user-transaction")
router.register('webhooks/test', WebhookTestViewset, basename='webhook-test')

# Register Viewsets here
urlpatterns = router.urls + []