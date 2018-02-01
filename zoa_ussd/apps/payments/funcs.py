from django.db import transaction as db_transaction
from django.db.models import Sum
from django.conf import settings

from camara_coupons.apps.coupons import funcs as coupon_funcs
from camara_coupons.apps.sms import funcs as sms_funcs

from camara_coupons.apps.coupons.models import Coupon, Course
from camara_coupons.apps.users.models import CamaraUser

from .models import FlutterwaveCustomer, FlutterwavePayment, MpesaTransaction, CouponIssue
from decimal import Decimal as D
import requests

def get_coupon_issues(limit=20):
    return CouponIssue.objects.order_by('-created_at')

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
