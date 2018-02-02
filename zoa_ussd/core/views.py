import json
import random

from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse

@login_required
def index(request):
    return TemplateResponse(request, "index.html", {
    })

def starter(request):
    return TemplateResponse(request, "starter.html", {
    })    

def mobile_phone(request):
    return TemplateResponse(request, "mobile_phone.html", {
    })