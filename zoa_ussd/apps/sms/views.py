from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render_to_response, redirect, render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import funcs, forms

import json

@login_required
def send_sms(request):
    success = False

    if request.method == "POST":
        funcs.send_sms()
    else:
        pass

    return JsonResponse({
        "success": success
    })

@csrf_exempt
def sms_received(request):

    if request.method == "POST":
        form = forms.SMSReceivedForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            funcs.receive_sms(
                message_id=data.get("message_id"),
                link_id=data.get("link_id"),
                message_from=data.get("message_from"),
                to=data.get("to"),
                text=data.get("text"),
                date=data.get("date"))

    return JsonResponse({

    })

@csrf_exempt
def sms_delivered(request):
    if request.method == "POST":
        status = request.POST.get('status')
        message_id = request.POST.get('id')
        failure_reason = None

        if status and message_id:
            #This parameter is passed when status is Rejected or Failed.
            if status in ("Failed", "Rejected"):
                failure_reason = request.POST.get('failureReason')

            funcs.mark_sms_delivered(message_id, status, failure_reason=failure_reason)

    return JsonResponse({

    })