import json
import urllib2

from django.conf import settings
from django.db import transaction as db_transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseServerError
from django.http.request import QueryDict
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..coupons import funcs as coupon_funcs
from ..coupons.models import Coupon, Course

from . import funcs as payment_funcs
from .models import FlutterwaveCustomer, FlutterwavePayment, CouponIssue, MpesaTransaction

@csrf_exempt
def start_flutterwave_payment(request):
    success = False

    if request.method == "POST":
        entity_first_name = None
        entity_last_name = None
        entity_account_number = None
        entity_card6 = None
        entity_card_last4 = None

        try:
            payload_qdict = QueryDict(request.body)
            payload = payload_qdict.dict()
            
            if not (payload["flwRef"] == "N/A"):
                return end_flutterwave_payment(request)

            print payload
        except ValueError as e:
            print e
            return HttpResponseServerError(e.message)

        if 'entity[card6]' in payload:
            entity_card6 = payload["entity[card6]"]
            entity_card_last4 = payload["entity[card_last4]"]
        elif "entity[account_number]" in payload:
            entity_first_name = payload["entity[first_name]"]
            entity_last_name = payload["entity[last_name]"]
            entity_account_number = payload["entity[account_number]"]

        with db_transaction.atomic():
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
            course_id = None
            mpesa_response_gotten = False
            meta_list = transaction_details.get("data", {}).get("meta", [])
            for meta in meta_list:
                if meta["metaname"] == "Course ID":
                    course_id = meta["metavalue"]

            payment = FlutterwavePayment.objects.create(
                entity_first_name=entity_first_name,
                entity_last_name=entity_last_name,
                entity_account_number=entity_account_number,
                entity_card6=entity_card6,
                entity_card_last4=entity_card_last4,
                txId=payload["id"],
                course_id=course_id,
                txRef=payload["txRef"],
                currency=payload["currency"],
                charged_amount=payload["charged_amount"],
                amount=payload["amount"],
                status=payload["status"],
                ip_address=payload["IP"])
            success = True

    return JsonResponse({ "success": success })

@csrf_exempt
def end_flutterwave_payment(request):
    response = None

    if request.method == "POST":
        payload = None
        try:
            payload_qdict = QueryDict(request.body)
            payload = payload_qdict.dict()
            print payload
        except ValueError as e:
            print e
            raise Http404

        with db_transaction.atomic():
            transaction_details = payment_funcs.get_transaction_details(payload["txRef"])

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
            if payment.course_id is not None:
                coupon, sms_sent = coupon_funcs.issue_coupon(
                    payment.course_id, (mpesa_transaction.phone if mpesa_transaction else None))
                if coupon is not None:
                    customer = get_object_or_404(FlutterwaveCustomer, fw_customer_id=payload["customer[id]"])
                    coupon_issue = CouponIssue.objects.create(
                        coupon_issued=coupon,
                        issued_to=customer,
                        payment=payment,
                        sms_sent=sms_sent.pop(0) if sms_sent else None,
                        course=coupon.course)
                    response = {"success": True}

            payment.mpesa_transaction = mpesa_transaction
            payment.status = payload["status"]         
            payment.raw_json = json.dumps(transaction_details)
            payment.flwRef = payload["flwRef"]
            payment.save()

    if response is None:
        response = {"success": False}
    return JsonResponse(response)