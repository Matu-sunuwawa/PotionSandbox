from django.contrib import admin

from .models import *


class TransactionAdmin(admin.ModelAdmin):
    list_display = ["account","amount","transaction_type","balance_after_transaction"]

admin.site.register(Transaction, TransactionAdmin)

