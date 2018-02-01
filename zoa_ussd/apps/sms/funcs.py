from decimal import Decimal as D

from django.utils import timezone, timesince
from django.db import transaction as db_transaction

try:
    from africastalking.AfricasTalkingGateway import \
        AfricasTalkingGateway, AfricasTalkingGatewayException
except ImportError:
    from AfricasTalkingGateway import \
        AfricasTalkingGateway, AfricasTalkingGatewayException

from .models import SMSGateway, SMSMessage, Template

def get_no_of_sms_sent():
    no_of_sms = SMSMessage.objects.filter(
        message_type=SMSMessage.SMS_OUT,
        status=SMSMessage.SUCCESS,
        delivered=True
    ).count()

    return no_of_sms

def render_to_sms(template_code, kwargs):
    template = Template.objects.filter(code=template_code).first()
    if template is not None:
        try:
            return template.template_text % kwargs
        except:
            return template.template_text 

    raise Exception("Please set up template #%s" % template_code)

def receive_sms(
    message_id=None, 
    link_id=None, 
    message_from=None, 
    message_to=None, 
    text=None, 
    date=None,
    gateway=SMSGateway.AFRICAS_TALKING):
    
    sms_message = SMSMessage.objects.create(
        sms_gateway=gateway,
        message_type=SMSMessage.SMS_IN,
        message=text,
        sender_id=message_from,
        recipient_id=message_to,
        status=SMSMessage.SUCCESS)

    return sms_message

def mark_sms_delivered(message_id, status, failure_reason=None, time_delivered=None):
    SMSMessage.objects.filter(
        message_id=message_id
    ).update(
        status=(SMSMessage.SUCCESS if status in ("success", "Success") else SMSMessage.ERROR),
        at_delivery_status=status,
        at_delivery_failure_reason=failure_reason,
        delivered=(failure_reason is None),
        time_delivered=time_delivered or timezone.now()
    )

def send_sms(
    to=None, 
    message=None, 
    gateway=SMSGateway.AFRICAS_TALKING, 
    template=None, 
    template_args=None
):
    """
    Send 
    """
    if to is None:
        to = []

    sms_sent = []
    
    with db_transaction.atomic():
        sms_gateway = SMSGateway.objects.filter(
            service_provider=gateway
        ).first()
        
        if sms_gateway is None:
            raise Exception("Setup SMS gateway first!")

        # Create a new instance of our awesome gateway class
        args = (sms_gateway.api_key, sms_gateway.api_secret)
        if sms_gateway.is_sandbox:
            args += ("sandbox",)

        africas_talking_gateway = AfricasTalkingGateway(*args)

        if message is None and (template and template_args):
            try:
                message = template.template_text % template_args
            except:
                message = template.template_text
        
        # Thats it, hit send and we'll take care of the rest.
        results = africas_talking_gateway.sendMessage(
            to, message, (sms_gateway.short_code or sms_gateway.sender_id)
        )
        
        for result in results:
            sms_message = SMSMessage(
                sms_gateway=sms_gateway,
                message_type=SMSMessage.SMS_OUT)

            # status is either "Success" or "error message"
            sms_message.message = message
            sms_message.recipient_id = result['number']

            sms_message.sender_id = \
                sms_gateway.short_code or sms_gateway.sender_id or "system"

            sms_message.status = SMSMessage.SUCCESS \
                if result['status'] in ("success", "Success") else SMSMessage.ERROR
            
            sms_message.message_id = result['messageId']
            sms_message.cost = result['cost']

            sms_message.save()
            sms_sent.append(sms_message)

    return sms_sent
