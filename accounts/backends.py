from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class PhoneAuthenticationBackend(ModelBackend):
    def authenticate(self, request, password, phone_number=None, username=None):

        if not phone_number:
            phone_number = username

        user = User.objects.filter(phone_number=phone_number.strip()).first()

        if user and user.check_password(password) and user.is_phone_verified:
            return user