dojoConfig = {parseOnLoad: true}
require([
    "dojo/parser",
    "dojox/form/CheckedMultiSelect",
    "dijit/form/Button",
    "dijit/form/DateTextBox", 
    "dijit/layout/BorderContainer", 
    "dojox/form/CheckedMultiSelect", 
    "dijit/layout/TabContainer", 
    "dijit/layout/ContentPane", 
    "dijit/layout/AccordionPane"
]);

var map;

function init(farmer_location) {
    map = new OpenLayers.Map("map-id", {
        controls: [
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.LayerSwitcher({'div':OpenLayers.Util.getElement('layerswitcher')}),
            new OpenLayers.Control.ScaleLine()
        ]
    });


    var map_center     = new OpenLayers.LonLat(37.002603550247592,-1.25793);
    var map_zoom_level = 15;
    
    // add layers
    var map_base_layer = new OpenLayers.Layer.WMS("OpenStreetMap WMS",
        "https://ows.terrestris.de/osm/service?",
        {layers: 'OSM-WMS'},{isBaseLayer: true}
    );

    var markers = new OpenLayers.Layer.Markers("My Location");
    
    var size = new OpenLayers.Size(36, 36);
    var icon = new OpenLayers.Icon('/static/img/marker.png', size);

    markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(
        farmer_location.coordinates[0], farmer_location.coordinates[1]
    ), icon));
  
    map.addLayers([map_base_layer, markers]);
    map.setCenter(map_center, map_zoom_level);

    //supplier layer
    var supplier_style = new OpenLayers.Style({
        // the first argument is a base symbolizer
        // all other symbolizers in rules will extend this one
        strokeColor: "red",
        strokeWidth: 3,
        fillColor:'red',
        pointRadius: 4,
        strokeOpacity: 1,
        fillOpacity : 2                                        
    });         
                
    var supplier_stylemap = new OpenLayers.StyleMap({
        'default': supplier_style
    });
    // Define the GeoJSON layer
    var supplier_stlayer = new OpenLayers.Layer.Vector("Suppliers", {
        projection: 'EPSG:32737',
        strategies: [
            new OpenLayers.Strategy.Fixed()
        ],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "/suppliers.geojson",
            format: new OpenLayers.Format.GeoJSON()
        }),
        styleMap: supplier_stylemap
    });
    map.addLayers([
        supplier_stlayer
    ]);
                
    var selectCtrl = new OpenLayers.Control.SelectFeature(supplier_stlayer);
            
    function createPopup(feature) {
        //var url = ' "src/geoext/resources/GeoEXT/Signage1.JPG" '
        var bogusMarkup = "<strong> SUPPLIER CATEGORY : </strong> " + feature.attributes.ItemName + 
        "</br> <strong> NAME : <strong> " + feature.attributes.Name+
        "</br> <strong> PHONE NUMBER : <strong> " + feature.attributes.Contact;
        
        popup = new GeoExt.Popup({
            title: 'FEATURE PROPERTIES',
            location: feature,
            width:300,
            height:150,
            html: bogusMarkup,
            maximizable: true,
            collapsible: true
        });
        // unselect feature when the popup
        // is closed
        popup.on({
            close: function() {
                if(OpenLayers.Util.indexOf(supplier_stlayer.selectedFeatures,
                                           this.feature) > -1) 
                {
                    selectCtrl.unselect(this.feature);
                }
            }
        });
        popup.show();
    }

    // create popup on "featureselected"
    supplier_stlayer.events.on({
        featureselected: function(e) {
            createPopup(e.feature);
        }
    });
    
    map.addControl(selectCtrl);
    selectCtrl.activate();
        
    // create feature store, binding it to the vector parcel layer
    store = new GeoExt.data.FeatureStore({
        layer: supplier_stlayer,
        fields: [
            {name: 'ItemType', type: 'string'},
            {name: 'ItemName', type: 'string'},
            {name: 'Contact', type: 'string'},
            {name: 'Name', type: 'string'}
        ],
        proxy: new GeoExt.data.ProtocolProxy({
            protocol: new OpenLayers.Protocol.HTTP({
                url: "/suppliers.geojson",
                format: new OpenLayers.Format.GeoJSON()
            })
        })
    });

    // create grid panel configured with feature store
    gridPanel = new Ext.grid.GridPanel({
        title: "Suppliers Feature Grid",
        region: "center",
        store: store,
        height: 150,
        width: '100%',
        columns: [{
            header: "Type",
            width: 150,
            dataIndex: "ItemType"
        },{
            header: "Category",
            width: 150,
            dataIndex: "ItemName"
        }, {
            header: "Name",
            width: 150,
            dataIndex: "Name"
        }, {
            header: "Phone number",
            width: 150,
            dataIndex: "Contact"
        }],
        sm: new GeoExt.grid.FeatureSelectionModel() 
    }); 
                
    // create a panel and add the map panel and grid panel
    // inside it
    mainPanel = new Ext.Panel({
        renderTo: "bottomPanel",
        //layout: "border",
        height: "185",
        width: "100%",
        items: [gridPanel]
    });

    $("#querySupplierLayerForm").submit(function(e){
        e.preventDefault();

        var form = e.target;
        formData = $(form).serialize();
        
        var supplierbyNameStyl;
        var Supplierbynamemap;
        var SupplierLayer;
        
        var service_name;
        var product_name;
        var itemType;

        if($("#product_item_type").is(':checked')) {
            product_name = $('input[name="product_name"]').val();
            itemType = 'product';
        } else {
            service_name = $('input[name="service_name"]').val();
            itemType = 'service';
        }

        supplierbyNameStyl = new OpenLayers.Style({
                strokeColor: 'yellow',
                strokeWidth: 3,
                fillColor:'orange',
                pointRadius: 8,
                strokeOpacity: 1,
                fillOpacity : 1
            }, {
                rules: [
                    new OpenLayers.Rule({
                        filter: new OpenLayers.Filter.Comparison({
                            type: OpenLayers.Filter.Comparison.LIKE,
                            property: "ItemName",
                            value: service_name || product_name
                        })
                    }),
                    new OpenLayers.Rule({
                        filter: new OpenLayers.Filter.Comparison({
                            type: OpenLayers.Filter.Comparison.LIKE,
                            property: "ItemType",
                            value: itemType
                        })
                    })
                ]
            }
        );
        Supplierbynamemap = new OpenLayers.StyleMap({'default': supplierbyNameStyl});
        // Define the GeoJSON layer
        SupplierLayer = new OpenLayers.Layer.Vector("Query: " + itemType + " = " + (service_name || product_name) , {
           //projection: toProjection,
           strategies: [new OpenLayers.Strategy.Fixed()],
           protocol: new OpenLayers.Protocol.HTTP({
              url: "/suppliers.geojson?" + formData,
              format: new OpenLayers.Format.GeoJSON()
           }),
           styleMap: Supplierbynamemap
        });

        map.addLayers([SupplierLayer]);
    });
    $('#product_item_type').change(function(e){
        e.preventDefault();
        if($(this).is(':checked')){
            $('.product-items').removeClass("hidden");
            $('.service-items').addClass("hidden");
        }
    });
    $('#service_item_type').change(function(e){
        e.preventDefault();
        if($(this).is(':checked')){
            $('.product-items').addClass("hidden");
            $('.service-items').removeClass("hidden");
        }
    }); 
    $("#product_item_type").prop("checked", true);
    $('.service-items').addClass("hidden");
}