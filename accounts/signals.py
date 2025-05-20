import logging
from datetime import datetime, timedelta

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.utils import *

from .dispatch import *
from .models import TemporaryCode, User, VerificationCode

logger = logging.getLogger(__name__)


@receiver(user_registered, sender=User)
def upon_registration(sender, instance, method, **kwargs):

    print("Generating Verification Codes...")
    print(kwargs)

    code = str(generate_secure_six_digits())

    if method == "EMAIL":

        VerificationCode.objects.create(
            user=instance,
            token=code,
            expires_at=datetime.now() + timedelta(minutes=5),
            code_type=2,
        )

    else:
        VerificationCode.objects.create(
            user=instance,
            token=code,
            expires_at=datetime.now() + timedelta(minutes=5),
            code_type=1,
        )
        TemporaryCode.objects.create(phone_number=instance.phone_number, code=code)