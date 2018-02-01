from __future__ import unicode_literals

from django.db import models

class SMSGateway(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)

    AFRICAS_TALKING = 1
    SERVICE_PROVIDERS = (
        (AFRICAS_TALKING, "Africa's Talking"),)
    service_provider = models.IntegerField(
        choices=SERVICE_PROVIDERS, null=True, blank=False)

    api_key    = models.CharField(max_length=100,
        help_text="For Africas' Talking, this is the username")
    api_secret = models.CharField(max_length=100, 
        help_text="For Africas' Talking, this is the api key")

    is_sandbox = models.NullBooleanField()

    short_code = models.CharField(max_length=20, null=True, blank=True)
    sender_id  = models.CharField(max_length=20, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "[%s] %s" % (self.code, self.name)

class Template(models.Model):
    ISSUE_COUPON = "001"
    ERROR_ISSUING_COUPON = "002"
    COUPON_REDEEMED = "003"
    TEMPLATE_CODES = (
        (ISSUE_COUPON, "Issue coupon"),
        (ERROR_ISSUING_COUPON, "Error issuing coupon"),
        (COUPON_REDEEMED, "Coupon redeemed"))

    label = models.CharField(max_length=100) 
    code = models.CharField(max_length=20)

    template_text = models.CharField(max_length=400)
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "[%s] %s" % (self.code, self.label)

class SMSMessage(models.Model):
    template = models.ForeignKey('Template', null=True)
    sms_gateway = models.ForeignKey('SMSGateway')

    SMS_IN = 1
    SMS_OUT = 2
    MESSAGE_TYPES = (
        (SMS_IN, "SMS IN"),
        (SMS_OUT, "SMS OUT"))
    message_type = models.IntegerField(choices=MESSAGE_TYPES)

    message = models.CharField(max_length=480)

    
    # Set the sender ID as "system" to 
    # refer to message sent by system
    sender_id = models.CharField(max_length=50)
    message_id = models.CharField(max_length=50, null=True)
    recipient_id = models.CharField(max_length=50)

    cost = models.CharField(max_length=30, null=True)

    SUCCESS = 1
    ERROR = 2
    STATUSES = (
        (SUCCESS, "Success"),
        (ERROR, "Error"))
    status = models.IntegerField(choices=STATUSES, null=True)

    #Flags specific to africa's talking
    DELIVERY_STATUSES = [
        ("Sent", "The message has successfully been sent by our network."),
        ("Submitted", "The message has successfully been submitted to the MSP (Mobile Service Provider)."),
        ("Buffered", "The message has been queued by the MSP."),
        ("Rejected", "The message has been rejected by the MSP. This is a final status."),
        ("Success", "The message has successfully been delivered to the receiver's handset. This is a final status."),
        ("Failed", "The message could not be delivered to the receiver's handset. This is a final status.")
    ]
    at_delivery_status = models.CharField(max_length=9, choices=DELIVERY_STATUSES, null=True)
    DELIVERY_FAILURE_REASONS = [
        ("InsufficientCredit", "This occurs when the subscriber don't have enough airtime for a premium subscription service/message"),
        ("InvalidLinkId", "This occurs when a message is sent with an invalid linkId for an onDemand service"),
        ("UserIsInactive", "This occurs when the subscriber is inactive or the account deactivated by the MSP (Mobile Service Provider)."),
        ("UserInBlackList", "This would occur if the user has been blacklisted not to receive messages from a paricular service (shortcode or keyword)"),
        ("UserAccountSuspended", "This would occur when the mobile subscriber has been suspended by the MSP."),
        ("NotNetworkSubcriber", "This occurs when the message is passed to an MSP where the subscriber doesn't belong."),
        ("UserNotSubscribedToProduct", "This is for a subscription product which the subscriber has not subscribed to."),
        ("UserDoesNotExist", "This occurs when the message is sent to a non-existent mobile number."),
        ("DeliveryFailure", "This occurs when message delivery fails for any reason not listed above or where the MSP didn't provide a delivery failure reason."),
    ]
    at_delivery_failure_reason = models.CharField(max_length=26, choices=DELIVERY_FAILURE_REASONS, null=True)

    delivered = models.NullBooleanField()
    time_delivered = models.DateTimeField(null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "[%s] %s" % (self.sender_id, self.message)