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

class TempraryCodeAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "code", "user_id", "created_at"]

    def user_id(self, instance):
        user = User.objects.filter(phone_number=instance.phone_number).first()

        if user:
            return user.id

class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ["code_type", "user", "is_used", "expires_at"]

class UserBankAccountAdmin(admin.ModelAdmin):
    list_display = ["account_no","balance","account_type","gender","birth_date"]

class CentralBankAccountAdmin(admin.ModelAdmin):
    list_display = ["name","account_no","balance","created_at"]

class BankAccountTypeAdmin(admin.ModelAdmin):
    list_display = ["name","maximum_withdrawal_amount","annual_interest_rate","interest_calculation_per_year"]

class UserAddressAdmin(admin.ModelAdmin):
    list_display = ["street_address","city","postal_code","country","user_id"]

admin.site.register(User, UserAdmin)
admin.site.register(BankAccountType, BankAccountTypeAdmin)
admin.site.register(UserBankAccount, UserBankAccountAdmin)
admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(VerificationCode, VerificationCodeAdmin)
admin.site.register(TemporaryCode, TempraryCodeAdmin)
admin.site.register(CentralBankAccount, CentralBankAccountAdmin)