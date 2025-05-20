# DEPOSIT = 1
# WITHDRAWAL = 2
# INTEREST = 3
# TRANSFER = 4
# INTERBANK = 5

# PENDING = 1
# COMPLETED = 2
# FAILED = 3

TRANSACTION_TYPE_CHOICES = (
    ('DEPOSIT', 'Deposit'),
    ('WITHDRAWAL', 'Withdrawal'),
    ('INTEREST', 'Interest'),
)

TRANSACTION_TYPES = [
    ('DEPOSIT', 'Deposit'),
    ('WITHDRAWAL', 'Withdrawal'),
    ('INTERBANK', 'Interbank Transfer'),
    ('INTRABANK', 'Intrabank Transfer')
]

STATUS_TYPES = [
    ('PENDING', 'Pending'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed')
]