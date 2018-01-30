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

function init() {
    map = new OpenLayers.Map("map-id", {
        controls: [
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.LayerSwitcher({'div':OpenLayers.Util.getElement('layerswitcher')}),
            new OpenLayers.Control.ScaleLine()
        ]
    });

    var map_center         = new OpenLayers.LonLat(36.99371,-1.25793);
    var map_zoom_level     = 15; 
    
    // add layers
    var map_base_layer = new OpenLayers.Layer.WMS("OpenStreetMap WMS",
        "https://ows.terrestris.de/osm/service?",
        {layers: 'OSM-WMS'},{isBaseLayer: true}
    );
  
    map.addLayers([map_base_layer]);
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
    var supplier_stlayer = new OpenLayers.Layer.Vector("Supplier_GJson", {
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
        var bogusMarkup = "<strong> SUPPLIER CATEGORY : </strong> " + feature.attributes.Name + 
        "</br> <strong> NAME : <strong> " + feature.attributes.Name_+
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
            {name: 'Name', type: 'string'},
            {name: 'Contact', type: 'float'},
            {name: 'Name_', type: 'string'}
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
            header: "Category",
            width: 150,
            dataIndex: "Name"
        }, {
            header: "Name",
            width: 150,
            dataIndex: "Name_"
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
        height: "150",
        width: "100%",
        items: [gridPanel]
    });

    $("#querySupplierLayerForm").submit(function(e){
        e.preventDefault();

        var form = e.target;
        formData = $(form).serialize();
        
        var supplierbyNameStyl = new OpenLayers.Style({
           // the first argument is a base symbolizer
           // all other symbolizers in rules will extend this one
              strokeColor: 'yellow',
              strokeWidth: 3,
              fillColor:'orange',
              pointRadius: 8,
              strokeOpacity: 1,
              fillOpacity : 1
              //graphicYOffset: 0, // shift graphic up 28 pixels
            }, // the second argument is the set of rules
            {
                rules: [
                    new OpenLayers.Rule({
                        filter: new OpenLayers.Filter.Comparison({
                        type: OpenLayers.Filter.Comparison.LIKE,
                        property: "Name",
                        value: valueSupplierName})
                     })
                ]}
        );
        var Supplierbynamemap = new OpenLayers.StyleMap({'default': supplierbyNameStyl});
        // Define the GeoJSON layer
        var SupplierLayer = new OpenLayers.Layer.Vector("Query: Supplier = " + valueSupplierName, {
           //projection: toProjection,
           strategies: [new OpenLayers.Strategy.Fixed()],
           protocol: new OpenLayers.Protocol.HTTP({
              url: "/suppliers.geojson?" + formData,
              format: new OpenLayers.Format.GeoJSON()
           }),
           styleMap: Supplierbynamemap
        });

        $.each(map.graphicsLayerIds, function(index, value){
            map.removeLayer(map.getLayer(value));
        });
        map.addLayers([SupplierLayer]);
    });
}   //close function init(){}
