from django.db import models


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
