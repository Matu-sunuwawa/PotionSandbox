from django.contrib import admin

from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "phone_number",
        "first_name",
        "last_name",
        "is_phone_verified",
    ]

class BankAccountAdmin(admin.ModelAdmin):
    list_display = ["account_number","branch","account_type","balance","owner"]


admin.site.register(User, UserAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
