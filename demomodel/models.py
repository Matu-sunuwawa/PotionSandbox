# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class NBECentralBank(models.Model):
    total_reserves = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    base_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    last_policy_update = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "National Bank of Ethiopia"
    
    def __str__(self):
        return "National Bank of Ethiopia"

class CommercialBank(models.Model):
    BANK_TYPES = [
        ('CBE', 'Commercial Bank of Ethiopia'),
        ('AWASH', 'Awash Bank'),
        ('DASHEN', 'Dashen Bank'),
        ('OTHER', 'Other')
    ]
    
    name = models.CharField(max_length=100, unique=True)
    license_number = models.CharField(max_length=20, unique=True)
    swift_code = models.CharField(max_length=11, unique=True)
    established_date = models.DateField()
    reserve_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    bank_type = models.CharField(max_length=20, choices=BANK_TYPES)
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

class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('SAVINGS', 'Savings Account'),
        ('CHECKING', 'Checking Account'),
        ('FOREIGN', 'Foreign Currency Account')
    ]
    
    account_number = models.CharField(max_length=20, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='ETB')
    opened_date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.account_number} - {self.owner.get_full_name()}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
        ('INTERBANK', 'Interbank Transfer')
    ]
    
    source_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='sent_transactions')
    destination_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    nbe_settlement_ref = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class InterbankSettlement(models.Model):
    sender_bank = models.ForeignKey(CommercialBank, on_delete=models.CASCADE, related_name='sent_settlements')
    receiver_bank = models.ForeignKey(CommercialBank, on_delete=models.CASCADE, related_name='received_settlements')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    settlement_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ], default='PENDING')

    def __str__(self):
        return f"Settlement {self.reference_number} - {self.amount}"