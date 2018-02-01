from .default import *

ALLOWED_HOSTS = [
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'camara',
        'HOST': 'localhost',
        'USER': 'camara',
        'PASSWORD': 'camara',
    }
}
DEBUG = True

try:
    from .local import *
except ImportError:
    pass