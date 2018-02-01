from django.contrib import admin

from .models import SMSGateway, Template, SMSMessage

@admin.register(SMSGateway)
class SMSGatewayAdmin(admin.ModelAdmin):
    list_display = (
        "name", "code", "service_provider", 
        "api_key", "api_secret", "is_sandbox", 
        "short_code", "sender_id"
    )
    list_filter = ('is_sandbox', "service_provider")
    search_fields = ("name", "code", "service_provider",)
    ordering = ('created_at',)

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('label', 'code', 'template_text')
    list_filter = ('label',)
    search_fields = ('label', 'code', 'template_text',)
    ordering = ('created_at',)

@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = (
        'sms_gateway',
        'message_type',
        'sender_id',
        'recipient_id',
        'status',
        'at_delivery_status',
        'delivered'
    )
    list_filter = ('status',)
    ordering = ('created_at',)
