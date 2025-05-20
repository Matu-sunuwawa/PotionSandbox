from django.contrib import admin

from .models import *

class NBECentralBankAdmin(admin.ModelAdmin):
    list_display = ["total_reserves","base_interest_rate","last_policy_update"]

class CommercialBankAdmin(admin.ModelAdmin):
    list_display = ["name","reserve_balance"]

class BranchAdmin(admin.ModelAdmin):
    list_display = ["commercial_bank","location","contact_number"]

admin.site.register(NBECentralBank, NBECentralBankAdmin)
admin.site.register(CommercialBank, CommercialBankAdmin)
admin.site.register(Branch, BranchAdmin)
