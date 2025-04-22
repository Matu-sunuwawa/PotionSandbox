from django.contrib import admin
from .models import *

admin.site.register(NBECentralBank)
admin.site.register(CommercialBank)
admin.site.register(Branch)
admin.site.register(BankAccount)
admin.site.register(Transaction)
admin.site.register(InterbankSettlement)
