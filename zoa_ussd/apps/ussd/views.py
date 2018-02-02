import json
import random

from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from django.http import JsonResponse, HttpResponse

from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from .models import *

def get_session_id(limit=10):
    chosen_chars   = ""
    possible_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    #Loop while letter count is less than limit
    while len(chosen_chars) <= limit:
        #get a random char from possible chars and concatinate it to the chosen chars
        chosen_chars = (chosen_chars + random.choice(possible_chars))

        if chosen_chars == '0': 
            #Shouldn't start with a zero, if it does, 
            #recursively call the get_session_id again to start all over
            return get_session_id(limit=limit)

    return chosen_chars

def get_ussd_response(
    input_value=None, 
    session_id=None, 
    phone_number=None
):
    response = "" 
    
    if session_id is None:
        session_id = get_session_id()

    #Validate to see that the main variables have values
    if phone_number is None:
        response = "Sorry, your request could not be processed. Please try again."
        return (response, None)

    #Get the USSDRequest object or create it if does not exist, set the ussd_object_created as False
    (ussd_request_obj, ussd_object_created) = USSDRequest.objects.get_or_create(
        session_id=session_id
    )

    # If the ussd request has been closed before, return nothing
    # This is to avoid updating a closed request
    if (ussd_request_obj.request_closed):
        response = "Session closed, Please try again."
        return (response, None)

    #get meu_step and last_menu_step from the ussd_request
    menu_step = last_menu_step = ussd_request_obj.last_step

    #if ussd_request_object has not been 
    if not ussd_object_created:
        menu_step = (last_menu_step + 1)
    elif ussd_object_created:
        #if the last menu_step is between 2, 3 and 4
        if last_menu_step in (
            USSDRequest.MENU_SERVICE,
            USSDRequest.MENU_PRODUCT_SERVICE_CATEGORY,
            USSDRequest.MENU_PRODUCT,
        ):
            if int(input_value) == 99:
                menu_step -= 1
            elif int(input_value) == 100:
                menu_step =  USSDRequest.MENU_USER_TYPE

    try:
        #Using the phone number provided by the Mobile Operator / Simulator, get the user
        request_user = User.objects.get(mobile_phone_number=phone_number)
        ussd_request_obj.user = request_user
    except User.DoesNotExist:
        #If no user exists, set as None, we will check to decide whether to register
        request_user = None

    if (request_user is None) and (menu_step > USSDRequest.MENU_FIRST):
        return (response, ussd_request_obj)

    # STEP 0:
    # We provide a welcome message for the user
    elif menu_step == USSDRequest.MENU_FIRST:
        if request_user is not None: # We know the user, so, we prompt for authentication
            response = (("Welcome %s, Please enter your PIN number to get started") % request_user.name)
        else:
            #We dont know the user, so, lets ask them to call us
            response = (
                "You do not have an account with us. Contact 0724158671 to register"
            )
            ussd_request_obj.request_closed = True

    #STEP 1.
    # The User has provide us with the PIN Number
    elif menu_step == USSDRequest.MENU_USER_TYPE:
        pin_number  = input_value

        #Lets check if the PIN number matches the User's PIN
        if request_user.pin_number == pin_number:
            response = (
                "You are a? \n"
                "1. Farmer\n"
                "2. Supplier\n"
            )
        else:
            #The PINs dont match, possibly not the owner
            response = "The PIN you have provided is not valid. Try again."
            return (response, ussd_request_obj)

    #STEP 2:
    # We already know the user type, lets check the services
    elif menu_step == USSDRequest.MENU_SERVICE:
        user_type = int(input_value)

        if user_type in (USSDRequest.FARMER_USER, USSDRequest.SUPPLIER_USER): #farmer
            response = "You are looking for? \n" if (user_type == 1) else "What do you provide? \n"
            response += (
                "1. Product \n"
                "2. Service \n"
                "0. Back \n"
                "00. Menu \n" 
            )

            #Set the user type
            ussd_request_obj.user_type = int(user_type)

    elif menu_step == USSDRequest.MENU_PRODUCT_SERVICE_CATEGORY:
        product_or_service = int(input_value)

        if product_or_service in (USSDRequest.PRODUCT_ORDER, USSDRequest.SERVICE_ORDER):
            if product_or_service == USSDRequest.PRODUCT_ORDER:
                product_types = []

                for p_type in ProductType.objects.all():
                    product_types.append("%s. %s" % (p_type.id, p_type.name))

                response = "%s%s%s%s" % (
                    "Product Category \n",
                    ("\n".join(product_types)),
                    "\n0. Back \n",
                    "00. Menu \n"
                )
            elif product_or_service == USSDRequest.SERVICE_ORDER:
                services = []

                for service in Service.objects.all():
                    services.append("%s. %s" % (service.id, service.name))

                response = "%s%s%s%s" % (
                    "Service \n",
                    "\n".join(services),
                    "\n0. Back \n",
                    "00. Menu \n"
                )

            ussd_request_obj.order_type = int(input_value)

    elif menu_step == USSDRequest.MENU_PRODUCT:
        if ussd_request_obj.order_type == USSDRequest.PRODUCT_ORDER:
            product_type_id = int(input_value)
            products = []   

            for product in Product.objects.filter(
                product_type__id=product_type_id
            ):
                products.append("%s. %s" % (product.id, product.name))

            response = "%s%s%s%s" % (
                "Select Product \n",
                "\n".join(products),
                "\n0. Back \n",
                "00. Menu \n"
            )

            ussd_request_obj.product_type_id = product_type_id
        elif ussd_request_obj.order_type == USSDRequest.SERVICE_ORDER:
            service_id = int(input_value)

            response = ("Your order has been received. Wait for an SMS response")

            ussd_request_obj.service_id = service_id
            ussd_request_obj.request_closed = True

            send_sms_to_nearby_suppliers(ussd_request_obj)

    elif menu_step == USSDRequest.MENU_QUANTITY:
        product_id = int(input_value)

        try:
            product = Product.objects.get(id=product_id)
            ussd_request_obj.product = product
            response = ("Enter quantity in %s" % product.get_unit_display())
        except Product.DoesNotExist:
            product = None
        
    elif menu_step == USSDRequest.MENU_PRICE:
        quantity = float(input_value)

        ussd_request_obj.quantity = quantity
        response = "Enter price per unit"

    elif menu_step == USSDRequest.MENU_LAST:
        price = float(input_value)

        ussd_request_obj.price = price
        ussd_request_obj.request_closed = True
        response = ("Your order has been received. Wait for an SMS response")

        # ussd_request_obj.save()

        send_sms_to_nearby_suppliers(ussd_request_obj)

    ussd_request_obj.last_step = menu_step
    ussd_request_obj.save()

    return (response, ussd_request_obj)

def ussd_request(request):
    '''
    This is a ussd request view, it receives a HTTP request object from Django Webserver
    Then, it checks through for values passed via the GET dictionary. We assume that 
    in every step, we will be provided with a session id, a menu_step and phone_number

    This view assists the user to create a USSDRequest object that will be used by 
    the system to create an order.
    '''
    response = ""

    if request.method == "GET":
        #Get the important values from the HTTP Request Object
        input_value    = request.GET.get('input_value')
        session_id     = request.GET.get('session_id')
        phone_number   = request.GET.get('phone_number')

        response = get_ussd_response(
            input_value=input_value,
            session_id=session_id,
            phone_number=phone_number
        )
    return HttpResponse(response)

def http_simulator(request):
    session_id = None
    phone_number = None
    request_closed = False

    if request.method == "GET":
        message = "Please enter your phone number to start"
    elif request.method == "POST":
        session_id   = request.POST.get('session_id')
        phone_number = request.POST.get('phone_number')
        input_value  = request.POST.get('input_value')

        if not USSDRequest.objects.filter(
            session_id=session_id,
            user__mobile_phone_number=phone_number
        ).exists():
            phone_number = input_value

        (message, ussd_request_obj) = get_ussd_response(
            input_value=input_value,
            session_id=session_id,
            phone_number=phone_number
        )

        session_id = ussd_request_obj.session_id
        phone_number = (
            ussd_request_obj.user.mobile_phone_number 
            if ussd_request_obj.user else phone_number
        )
        request_closed = ussd_request_obj.request_closed

    return TemplateResponse(request, "ussd.html", {
        "session_id": session_id,
        "phone_number": phone_number,
        "request_closed": request_closed,
        "message": message
    })