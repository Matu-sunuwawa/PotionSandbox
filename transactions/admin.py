from django.contrib import admin

from .models import *


# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ["account","amount","transaction_type","balance_after_transaction"]

class TransactionAdmin(admin.ModelAdmin):
    list_display = ["get_account_type", "amount", "transaction_type", "balance_after_transaction"]

    def get_account_type(self, instance):
        if instance.account:
            return f"{instance.account}"
        elif instance.central_account:
            return f"{instance.central_account}"
        return "No Account"

    get_account_type.short_description = "Account Type"

admin.site.register(Transaction, TransactionAdmin)

