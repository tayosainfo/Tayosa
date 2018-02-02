from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^receive/fw/start/$', views.start_flutterwave_payment, name="receive-payment-start"),
    url(r'^receive/fw/end/$', views.end_flutterwave_payment, name="receive-payment-end"),

    url(r'^receive/nifty/$', views.nifty_payment, name="nifty-payment")
]
