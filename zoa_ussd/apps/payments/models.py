from __future__ import unicode_literals

from django.db import models

class FlutterwaveCustomer(models.Model):
    full_name = models.CharField(max_length=100)

    email = models.EmailField(null=True)
    phone = models.CharField(max_length=100, null=True)

    customertoken = models.CharField(max_length=100, null=True)
    
    account_id = models.CharField(max_length=100, null=True)
    fw_customer_id = models.CharField(max_length=100, null=True)

    deleted_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return "%s %s" % (self.full_name, self.phone)

class FlutterwavePayment(models.Model):
    entity_first_name = models.CharField(max_length=100, null=True)
    entity_last_name = models.CharField(max_length=100, null=True)
    entity_account_number = models.CharField(max_length=100, null=True)

    entity_card6 = models.CharField(max_length=100, null=True)
    entity_card_last4 = models.CharField(max_length=100, null=True)

    flwRef = models.CharField(max_length=100, null=True)
    txId = models.CharField(max_length=100, null=True)
    txRef = models.CharField(max_length=100, null=True)

    currency = models.CharField(max_length=4)
    charged_amount = models.DecimalField(decimal_places=2, max_digits=18, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=18, null=True)

    status = models.CharField(max_length=20)
    ip_address = models.GenericIPAddressField()

    course_id = models.CharField(max_length=50, null=True)
    raw_json = models.CharField(max_length=5000, null=True, editable=True)
    mpesa_transaction = models.ForeignKey('MpesaTransaction', null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return "Payment flwRef:%s" % (self.flwRef)

    @property
    def is_card_payment(self):
        return None not in (self.entity_card6, self.entity_card_last4)

class MpesaTransaction(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    billref_number = models.CharField(max_length=30)
    fw_id = models.CharField(max_length=40)
    invoice_number = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=30, db_column="msisdn")
    thirdparty_transaction_id = models.CharField(max_length=30, null=True)
    transaction_amount = models.DecimalField(decimal_places=2, max_digits=18, null=True)
    transaction_id = models.CharField(max_length=30)
    transaction_time = models.CharField(max_length=30)

    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return "%s %s %s" % (self.transaction_id, self.phone, self.transaction_amount)
