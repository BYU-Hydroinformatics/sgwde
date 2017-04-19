/*****************************************************************************
 * FILE:    SGWDE MAIN.JS
 * DATE:    14 APRIL 2017
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) Brigham Young University 2017
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var SGWDE_PACKAGE = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
    var shpSource,shpLayer,layers,map;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var addDefaultBehaviorToAjax,$btnUpload,checkCsrfSafe,clear_coords,getCookie,get_plot,$get_plot,init_events,init_jquery_var,init_map,$modalUpload,prepare_files,upload_file;


    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
    init_jquery_var=function(){
        $get_plot = $('#get-plot');
        $modalUpload = $("#modalUpload");
        $btnUpload = $("#btn-add-shp");
    };
    init_events = function() {
        (function () {
            var target, observer, config;
            // select the target node
            target = $('#app-content-wrapper')[0];

            observer = new MutationObserver(function () {
                window.setTimeout(function () {
                    map.updateSize();
                }, 350);
            });
            $(window).on('resize', function () {
                map.updateSize();
            });

            config = {attributes: true};

            observer.observe(target, config);
        }());
    };
    clear_coords = function(){
        $("#poly-lat-lon").val('');
        $("#point-lat-lon").val('');
        $("#shp-lat-lon").val('');
    };
    init_map = function(){
        var projection = ol.proj.get('EPSG:3857');
        var baseLayer = new ol.layer.Tile({
            source: new ol.source.BingMaps({
                key: '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
                imagerySet: 'AerialWithLabels' // Options 'Aerial', 'AerialWithLabels', 'Road'
            })
        });
        shpSource = new ol.source.Vector();
        shpLayer = new ol.layer.Vector({
                    source: shpSource
                });
        var source = new ol.source.Vector({
            wrapX: false
        });
        var vector_layer = new ol.layer.Vector({
            name: 'my_vectorlayer',
            source: source,
            style: new ol.style.Style({
                fill: new ol.style.Fill({
                    color: 'rgba(255, 255, 255, 0.2)'
                }),
                stroke: new ol.style.Stroke({
                    color: '#ffcc33',
                    width: 2
                }),
                image: new ol.style.Circle({
                    radius: 7,
                    fill: new ol.style.Fill({
                        color: '#ffcc33'
                    })
                })
            })
        });
        var fullScreenControl = new ol.control.FullScreen();
        var view = new ol.View({
            center: [9500000, 2735000],
            projection: projection,
            zoom: 4
        });
        layers = [baseLayer,vector_layer];
        map = new ol.Map({
            target: document.getElementById("map"),
            layers: layers,
            view: view
        });
        map.addControl(new ol.control.ZoomSlider());
        map.addControl(fullScreenControl);
        map.crossOrigin = 'anonymous';
        var lastFeature, draw, featureType;
        var removeLastFeature = function () {
            if (lastFeature) source.removeFeature(lastFeature);
        };

        var addInteraction = function (geomtype) {
            var typeSelect = document.getElementById('types');
            var value = typeSelect.value;
            $('#data').val('');
            if (value !== 'None') {
                if (draw)
                    map.removeInteraction(draw);

                draw = new ol.interaction.Draw({
                    source: source,
                    type: geomtype
                });

                if (featureType === 'Point') {

                    draw.on('drawend', function (e) {
                        removeLastFeature();
                        lastFeature = e.feature;
                    });

                } else {

                    draw.on('drawend', function (e) {
                        lastFeature = e.feature;

                    });

                    draw.on('drawstart', function (e) {
                        source.clear();
                    });

                }
                map.addInteraction(draw);
            }


        };

        vector_layer.getSource().on('addfeature', function(event){
            var feature_json = saveData();
            var parsed_feature = JSON.parse(feature_json);
            var feature_type = parsed_feature["features"][0]["geometry"]["type"];
            if (feature_type == 'Point'){
                var coords = parsed_feature["features"][0]["geometry"]["coordinates"];
                var proj_coords = ol.proj.transform(coords, 'EPSG:3857','EPSG:4326');
                $("#point-lat-lon").val(proj_coords);

            } else if (feature_type == 'Polygon'){
                var coords = parsed_feature["features"][0]["geometry"]["coordinates"][0];
                proj_coords = [];
                coords.forEach(function (coord) {
                    var transformed = ol.proj.transform(coord,'EPSG:3857','EPSG:4326');
                    proj_coords.push('['+transformed+']');
                });
                var json_object = '{"type":"Polygon","coordinates":[['+proj_coords+']]}';
                $("#poly-lat-lon").val(json_object);
            }
        });
        function saveData() {
            // get the format the user has chosen
            var data_type = 'GeoJSON',
                // define a format the data shall be converted to
                format = new ol.format[data_type](),
                // this will be the data in the chosen format
                data;
            try {
                // convert the data of the vector_layer into the chosen format
                data = format.writeFeatures(vector_layer.getSource().getFeatures());
            } catch (e) {
                // at time of creation there is an error in the GPX format (18.7.2014)
                $('#data').val(e.name + ": " + e.message);
                return;
            }
            // $('#data').val(JSON.stringify(data, null, 4));
            return data;

        }

        $('#types').change(function (e) {
            featureType = $(this).find('option:selected').val();
            if(featureType == 'None'){
                $('#data').val('');
                clear_coords();
                map.removeInteraction(draw);
                vector_layer.getSource().clear();
                shpLayer.getSource().clear();
            }else if(featureType == 'Upload')
            {
                clear_coords();
                vector_layer.getSource().clear();
                shpLayer.getSource().clear();
                map.removeInteraction(draw);
                $modalUpload.modal('show');
            }else if(featureType == 'Point')
            {
                clear_coords();
                shpLayer.getSource().clear();
                addInteraction(featureType);
            }else if(featureType == 'Polygon'){
                clear_coords();
                shpLayer.getSource().clear();
                addInteraction(featureType);
            }
        }).change();
        init_events();

    };

    get_plot = function(){
        if($("#poly-lat-lon").val() == "" && $("#point-lat-lon").val() == "" && $("#shp-lat-lon").val() == ""){
            $('.warning').html('<b>No feature selected. Please create a feature using the map interaction dropdown. Plot cannot be generated without a feature.</b>');
            return false;
        }else{
            $('.warning').html('');
        }
        var datastring = $get_plot.serialize();
        $.ajax({
            type:"POST",
            url:'/apps/sgwde/get-plot/',
            dataType:'HTML',
            data:datastring,
            success:function(result){
                var json_response = JSON.parse(result);
                if(json_response.status === 'success'){
                    $(".plot").html('');
                    var png_file = json_response.png_file;
                    var img = document.createElement("IMG");
                    img.src = '/static/sgwde/wrf_plots/'+png_file;
                    img.height = "500";
                    img.width = "800";
                    document.getElementById('plot').appendChild(img);

                    $('#plotter').highcharts({
                        chart: {
                            type:'area',
                            zoomType: 'x'
                        },
                        title: {
                            text: json_response.var_name + " values at " +json_response.location,
                            style: {
                                fontSize: '11px'
                            }
                        },
                        xAxis: {
                            type: 'datetime',
                            labels: {
                                format: '{value:%d %b %Y}',
                                rotation: 45,
                                align: 'left'
                            },
                            title: {
                                text: 'Date'
                            }
                        },
                        yAxis: {
                            title: {
                                text: json_response.var_unit
                            }

                        },
                        exporting: {
                            enabled: true
                        },
                        series: [{
                            data:json_response.values,
                            name: json_response.variable
                        }]

                    });

                }
            }
        });
    };

    $("#btn-get-plot").on('click',get_plot);

    upload_file = function(){
        var files = $("#shp-upload-input")[0].files;
        var data;

        $modalUpload.modal('hide');
        data = prepare_files(files);

        $.ajax({
            url: '/apps/sgwde/upload-shp/',
            type: 'POST',
            data: data,
            dataType: 'json',
            processData: false,
            contentType: false,
            error: function (status) {
                console.log(status);
            }, success: function (response) {
                var extents = response.bounds;
                shpSource = new ol.source.Vector({
                    features: (new ol.format.GeoJSON()).readFeatures(response.geo_json)
                });
                shpLayer = new ol.layer.Vector({
                    name:'shp_layer',
                    extent:[extents[0],extents[1],extents[2],extents[3]],
                    source: shpSource,
                    style:new ol.style.Style({
                        stroke: new ol.style.Stroke({
                            color: 'blue',
                            lineDash: [4],
                            width: 3
                        }),
                        fill: new ol.style.Fill({
                            color: 'rgba(0, 0, 255, 0.1)'
                        })
                    })
                });
                map.addLayer(shpLayer);


                map.getView().fit(shpLayer.getExtent(), map.getSize());
                map.updateSize();
                map.render();

                var min = ol.proj.transform([extents[0],extents[1]],'EPSG:3857','EPSG:4326');
                var max = ol.proj.transform([extents[2],extents[3]],'EPSG:3857','EPSG:4326');
                var proj_coords = min.concat(max);
                $("#shp-lat-lon").val(proj_coords);

            }
        });


    };

    $("#btn-add-shp").on('click',upload_file);

    prepare_files = function (files) {
        var data = new FormData();

        Object.keys(files).forEach(function (file) {
            data.append('files', files[file]);
        });

        return data;
    };

    addDefaultBehaviorToAjax = function () {
        // Add CSRF token to appropriate ajax requests
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!checkCsrfSafe(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });
    };

    checkCsrfSafe = function (method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    getCookie = function (name) {
        var cookie;
        var cookies;
        var cookieValue = null;
        var i;

        if (document.cookie && document.cookie !== '') {
            cookies = document.cookie.split(';');
            for (i = 0; i < cookies.length; i += 1) {
                cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/


    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    $(function() {
        init_jquery_var();
        addDefaultBehaviorToAjax();
        init_map();


    });



}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.