import json
import requests

from django.conf import settings
from django.db import transaction as db_transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from zoa_ussd.apps.sms import funcs as sms_funcs

from .models import FlutterwaveCustomer, FlutterwavePayment, MpesaTransaction
from decimal import Decimal as D

def get_total_sales():
    return FlutterwavePayment.objects\
        .aggregate(total_sales=Sum('amount'))\
        .get('total_sales', D('0.0'))

def get_active_customers():
    return FlutterwaveCustomer.objects.filter(
        deleted_at__isnull=True
    ).count()

def get_transaction_details(txRef=None, fwRef=None):
    data = {
        "SECKEY": settings.FLUTTERWAVE_SECRET_KEY, #this is the secret key
        ("tx_ref" if txRef is not None else "fw_ref"): (txRef if txRef is not None else fwRef), 
        "normalize": "1"
    }

    url = "http://api.ravepay.co/flwv3-pug/getpaidx/api/verify"

    #make the http post request to our server with the parameters
    response = requests.post(url, headers={
            "Content-Type":"application/json"
        }, json=data)

    return response.json()

@db_transaction.atomic
def process_nifty_mpesa_transaction(payload):
    success = False

    print payload
    c2b_alert = json.loads(payload.get('Message'))
    print 'c2b_alert Data %s' % c2b_alert
    
    mpesa_transaction = MpesaTransaction.objects.create(
        phone=c2b_alert["MSISDN"],
        transaction_time=c2b_alert["TransTime"],
        billref_number=c2b_alert["BillRefNumber"],
        transaction_type=c2b_alert["TransType"],
        transaction_amount=c2b_alert["TransAmount"],
        transaction_id=c2b_alert["TransID"]

    for kyc_item in c2b_alert["KYCInfo"]:
        if kyc_item["KYCName"] == "[Personal Details][First Name]":
            mpesa_transaction.first_name = c2b_alert['KYCValue']
        elif kyc_item["KYCName"] == "[Personal Details][First Name]":
            mpesa_transaction.middle_name = c2b_alert['KYCValue']
        elif kyc_item["KYCName"] == "[Personal Details][First Name]":
            mpesa_transaction.last_name = c2b_alert['KYCValue']

    mpesa_transaction.save()

    nifty_transaction = NiftyTransaction.objects.create(
        mpesa_transaction=mpesa_transaction
        business_short_code=c2b_alert["BusinessShortCode"],
        org_account_balance=c2b_alert["OrgAccountBalance"])

    return success

@db_transaction.atomic
def process_flutterwave_start_mpesa_transaction(payload):
    success = False

    if 'entity[card6]' in payload:
        entity_card6 = payload["entity[card6]"]
        entity_card_last4 = payload["entity[card_last4]"]
    elif "entity[account_number]" in payload:
        entity_first_name = payload["entity[first_name]"]
        entity_last_name = payload["entity[last_name]"]
        entity_account_number = payload["entity[account_number]"]

    try:
        customer = FlutterwaveCustomer.objects.get(
            email=payload["customer[email]"])
    except FlutterwaveCustomer.DoesNotExist:
        try:
            customer, _ = FlutterwaveCustomer.objects.get_or_create(
                phone=payload["customer[phone]"],
                email=payload["customer[email]"],
                full_name=payload["customer[fullName]"],
                account_id=payload["customer[AccountId]"],
                updated_at=payload["customer[updatedAt]"],
                created_at=payload["customer[createdAt]"],
                customertoken=payload["customer[customertoken]"],
                fw_customer_id=payload["customer[id]"])

            if payload["customer[deletedAt]"]:
                customer.deleted_at = payload["customer[deletedAt]"]
                customer.save()
        except Exception as e:
            print e
            return HttpResponseServerError(e.message)

    transaction_details = payment_funcs.get_transaction_details(payload["txRef"])
    mpesa_response_gotten = False
    meta_list = transaction_details.get("data", {}).get("meta", [])

    payment = FlutterwavePayment.objects.create(
        entity_first_name=entity_first_name,
        entity_last_name=entity_last_name,
        entity_account_number=entity_account_number,
        entity_card6=entity_card6,
        entity_card_last4=entity_card_last4,
        txId=payload["id"],
        txRef=payload["txRef"],
        currency=payload["currency"],
        charged_amount=payload["charged_amount"],
        amount=payload["amount"],
        status=payload["status"],
        ip_address=payload["IP"])
    
    return success

@db_transaction.atomic
def process_flutterwave_end_mpesa_transaction(payload):
    transaction_details = payment_funcs.get_transaction_details(payload["txRef"])

    success = False
    mpesa_transaction = None
    mpesa_response_gotten = False
    meta_list = transaction_details.get("data", {}).get("meta", [])

    for meta in meta_list:
        if meta["metaname"] == "MPESARESPONSE" and not mpesa_response_gotten:
            mpesa_transaction_dict = json.loads(meta["metavalue"])

            try:
                kyc_info = mpesa_transaction_dict["kycinfo"]
                kyc_info = kyc_info.replace("[Personal Details][First Name]|", "")
                kyc_info = kyc_info.replace("[Personal Details][Last Name]|", "")
                first_name, last_name, _ = kyc_info.split(",")
            except Exception as e:
                print e
                first_name = last_name = None
            
            mpesa_transaction = MpesaTransaction.objects.create(
                first_name=first_name,
                last_name=last_name,
                billref_number=mpesa_transaction_dict["billrefnumber"],
                fw_id=mpesa_transaction_dict["id"],
                invoice_number=mpesa_transaction_dict["invoicenumber"],
                phone=mpesa_transaction_dict["msisdn"],
                thirdparty_transaction_id=mpesa_transaction_dict["thirdpartytransactionid"],
                transaction_amount=mpesa_transaction_dict["transactionamount"],
                transaction_id=mpesa_transaction_dict["transactionid"],
                transaction_time=mpesa_transaction_dict["transactiontime"])

            mpesa_response_gotten = True

    #import pdb; pdb.set_trace()
    payment = get_object_or_404(FlutterwavePayment, txId=payload["id"])
    customer = get_object_or_404(FlutterwaveCustomer, fw_customer_id=payload["customer[id]"])

    payment.mpesa_transaction = mpesa_transaction
    payment.status = payload["status"]         
    payment.raw_json = json.dumps(transaction_details)
    payment.flwRef = payload["flwRef"]
    payment.save()

    return success