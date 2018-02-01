from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'send/', views.send_sms, name="sms-send"),
    url(r'received/', views.sms_received, name="sms-received"),
    url(r'delivered/', views.sms_delivered, name="sms-delivered")
]
