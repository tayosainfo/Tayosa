from django.contrib import admin

from .models import *
from django.contrib.gis import admin

models = globals().copy()

for name, Model in models.iteritems():
    if hasattr(Model, '_meta') and not Model._meta.abstract and not 'UserProfile' == name:
        class Admin(admin.ModelAdmin):
            model = Model

            list_display = [f.name for f in Model._meta.fields]
            list_filter = [f.name for f in Model._meta.fields[5:]]
            list_per_page = 25

        admin.site.register(Model, Admin)

    elif name == 'Farmer' or name == 'Supplier':
        class Admin(admin.OSMGeoAdmin):
            model = Model
            list_display = ['name', 'geom']

            wms_url = 'https://ows.terrestris.de/osm/service?'
            wms_layer = 'OSM-WMS'
            wms_name = 'OpenLayers WMS'

        admin.site.register(Model, Admin)
