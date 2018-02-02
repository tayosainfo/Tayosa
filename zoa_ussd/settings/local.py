from .default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zoa_ussd',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '',
    }
}

DEBUG = True
FLUTTERWAVE_SECRET_KEY = "FLWSECK-113e139ff1c8b7dfa46b584864680e44-X"