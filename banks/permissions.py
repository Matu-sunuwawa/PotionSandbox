from rest_framework.permissions import BasePermission
from .models import AccessKey
from django.contrib.auth.hashers import check_password

class ExternalSysPermission(BasePermission):
    def has_permission(self, request, view):
        access_id = request.headers.get('X-Access-Id')
        access_secret = request.headers.get('X-Access-Secret')
        
        if not access_id or not access_secret:
            return False
            
        try:
            key = AccessKey.objects.get(access_id=access_id)
            return check_password(access_secret, key.access_secret)
        except AccessKey.DoesNotExist:
            return False