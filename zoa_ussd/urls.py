from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^starter/$', 'dairy.core.views.starter', name="starter"),
    url(r'^simulator/http/$', 'dairy.core.views.http_simulator', name="http-simulator"),

    url(r'^ussd.py$', 'dairy.core.views.ussd_request', name="ussd-request"),
    url(r'^suppliers.geojson$', 'dairy.core.views.suppliers_geojson', name="suppliers-geojson"),
    url(r'^$', 'dairy.core.views.index', name="index"),
    url(r'^mobile-phone/$', 'dairy.core.views.mobile_phone', name="mobile-phone"),
    
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
