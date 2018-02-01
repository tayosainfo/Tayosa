from __future__ import unicode_literals

from django.db import models

class USSDProvider(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)

    AFRICAS_TALKING = 1
    SERVICE_PROVIDERS = (
        (AFRICAS_TALKING, "Africa's Talking"),)
    service_provider = models.IntegerField(
        choices=SERVICE_PROVIDERS, null=True, blank=False)

    service_code = models.CharField(max_length=100)
    is_sandbox = models.NullBooleanField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ussd_provider"

class USSDPage(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)

    is_first = models.BooleanField(default=True)
    is_last  = models.BooleanField(default=True)

    step_no = models.IntegerField(null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ussd_page"

class USSDRequest(models.Model):
    session_id = models.CharField(max_length=100)
    provider   = models.ForeignKey("USSDProvider")

    current_page  = models.ForeignKey("USSDPage")
    previous_page = models.ForeignKey("USSDPage")

    user = models.ForeignKey('User', null=True)
    phone_number = models.CharField(max_length=100)

    text = models.CharField(max_length=100)
    request_closed = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ussd_request"
        unique_together = ('session_id', 'user')

    