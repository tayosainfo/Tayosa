from django.contrib import admin

from .models import FlutterwaveCustomer, FlutterwavePayment, MpesaTransaction

@admin.register(FlutterwaveCustomer)
class FlutterwaveCustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'customertoken', 'account_id', 'fw_customer_id',)
    search_fields = ('full_name', 'email', 'phone', 'customertoken', 'account_id', 'fw_customer_id',)
    ordering = ('created_at',)

@admin.register(FlutterwavePayment)
class FlutterwavePaymentAdmin(admin.ModelAdmin):
    list_display = (
        'flwRef', 'txId', 'txRef', 'course_id', 'currency', 
        'charged_amount', 'amount', 'status', 
        'ip_address', 'is_card_payment', 
    )
    list_filter = ('status',)
    search_fields = ('flwRef', 'txId', 'txRef', 'status', 'ip_address',)
    ordering = ('created_at',)

@admin.register(MpesaTransaction)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_time","transaction_id",
        "first_name","last_name",
        "phone","transaction_amount",
    )
    search_fields = ('transaction_id', 'first_name', 'last_name', 'phone',)
    ordering = ('created_at',)