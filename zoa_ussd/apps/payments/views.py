import json

from django.http import JsonResponse, Http404, HttpResponseServerError
from django.http.request import QueryDict

from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from . import funcs as payment_funcs

@csrf_exempt
def nifty_payment(request):
    success = True

    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            success = payment_funcs.process_nifty_mpesa_transaction(payload)
        except ValueError as e:
            print e
            raise Http404
        except Exception as e:
            print e
            return HttpResponseServerError(e.message)

    return JsonResponse(dict(success=success))

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

            success = payment_funcs.process_flutterwave_start_mpesa_transaction(payload)
        except ValueError as e:
            print e
            raise Http404
        except Exception as e:
            print e
            return HttpResponseServerError(e.message)

    return JsonResponse({"success": success})

@csrf_exempt
def end_flutterwave_payment(request):
    response = None

    if request.method == "POST":
        payload = None
        try:
            payload_qdict = QueryDict(request.body)
            payload = payload_qdict.dict()
            print payload
            response = payment_funcs.process_flutterwave_end_mpesa_transaction(payload)
        except ValueError as e:
            print e
            raise Http404
        except Exception as e:
            print e
            return HttpResponseServerError(e.message)

    if response is None:
        response = {"success": False}
    return JsonResponse(response)