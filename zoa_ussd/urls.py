from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

from core import views as core_views
from zoa_ussd.apps.ussd import views as ussd_views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^simulator/http/$', ussd_views.http_simulator, name="http-simulator"),
    url(r'^ussd.py$', ussd_views.ussd_request, name="ussd-request"),

    url(r'^$', core_views.index, name="index"),
    url(r'^starter/$', core_views.starter, name="starter"),
    url(r'^mobile-phone/$', core_views.mobile_phone, name="mobile-phone"),
    
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
