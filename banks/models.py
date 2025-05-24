
from uuid import uuid4
from django.db import models
from django.contrib.auth.hashers import check_password, make_password


class AccessKey(models.Model):
    access_id = models.CharField(max_length=255, unique=True)
    access_secret = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.access_id:
            self.access_id = str(uuid4().hex)

        self.access_secret = make_password(self.access_secret)
        super().save(*args, **kwargs)


class NBECentralBank(models.Model):
    total_reserves = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    base_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    last_policy_update = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "National Bank of Ethiopia"

class CommercialBank(models.Model):
    name = models.CharField(max_length=100, unique=True)
    license_number = models.CharField(max_length=20, unique=True)
    swift_code = models.CharField(max_length=11, unique=True)
    established_date = models.DateField()
    reserve_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    nbe = models.ForeignKey(NBECentralBank, on_delete=models.CASCADE, related_name='commercial_banks')
    access_key = models.OneToOneField(AccessKey, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Branch(models.Model):
    commercial_bank = models.ForeignKey(CommercialBank, on_delete=models.CASCADE, related_name='branches')
    branch_code = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    opened_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.commercial_bank.name} - {self.location}"
