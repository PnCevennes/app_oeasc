$(document).ready(function() {

  "use strict";


  var setBounds = function(bounds, map) {

    if(bounds.isValid()) {

      map.fitBounds(bounds);

    }

  };


  var deferred_setBounds = function(bounds, map) {

    setTimeout( setBounds, 500, bounds, map);

  };


  var f_tooltip = function(layer, map, fp) {

    var s_tooltip  = fp.area_name;

    layer.bindTooltip(s_tooltip, {opacity: 1, pane: 'PANE_' + M.style.pane.tooltips}).addTo(map);

  };


  var f_select = function(name, d_ls, layer, map) {

    var fp = layer.feature.properties;
    var ls = d_ls[name];

    map.fitBounds(layer.getBounds());

    f_add_feature_collection_to_map(map, name, fp);

  };


  // ajouter l'option au select
  var f_form = function(ls, layer, fp, map) {

    var $select_layer = $("#" + map.map_name);

    var s_option = '<option value="' + fp.id_area + '"> ' + fp.area_name + " </option>";
    $select_layer.append(s_option);

  };


  // pour chaque layer pendant le chargement ajax ( a refaire dans le data;loaded)

  var f_layer = function(name, d_ls, map) {

    return function(feature, layer) {

      var ls = d_ls[name];

      layer.setStyle(M.style.default);

      layer.setStyle({

        color: ls.color,
        fillColor: ls.color
      });

      var fp = feature.properties;

      fp.name = name;
      f_tooltip(layer, map, fp);
      f_form(ls, layer, fp, map);
      var s_label = f_label(ls, fp);

      layer.on("mouseover", function (e) {

        layer.setStyle(M.style.highlight);
        $("#infos_map").html(s_label);

      });

      layer.on("mouseout", function (e) {

        layer.setStyle(M.style.default);
        $("#infos_map").html("");

      });

      layer.on("click", function (e) {

        if(ls.next) {

          f_select(ls.next, d_ls, layer, map);

        }

        if(map.map_name == 'OEASC_DGD' || map.map_name == 'OEASC_ONF_FRT') {

          M.reset_foret();

        }

        f_select_layer(layer, map);

        $('#' + map.map_name).selectpicker();
        $('#' + map.map_name).selectpicker("render");

      });

    };

  };


  var f_change = function(map) { 
    return function(e) {

      // e.preventDefault();

      var $this = $(this);

      var values = $(this).val();

      if(values == "") {

        values=[];

      }

      else if( !(values instanceof Array) ) {

        values = [values];

      }

      // effacer les decochés encore selectionné sur carte

      get_layer_selected(map).forEach(function(_layer){

        var selected = false;

        $("#" + map.map_name + " :selected").each(function(i,e) {

          selected = (e.value == _layer.feature.properties.id_area || selected);

        });

        if(!selected) {

          var index = values.indexOf("" + _layer.feature.properties.id_area);

          if( index != -1 ) {

            values.splice(index, 1);

          }

          $this.val(values);
          M.f_select_layer(_layer, map);

        }

      });

      // ajouter les cochés pas encore selectionnés

      for(var i=0; i<values.length; i++) {

        var value = values[i];

        var l = M.get_layer(map, "id_area", value);

        if(!l) {

          continue;

        }

        if( !l.selected ) {

          M.f_select_layer(l, map);

        }

      }

    };

  };

  var f_select_layer = function(layer, map) {

    if(!layer) return false;

    var $select = $("#" + map.map_name);

    var fp = layer.feature.properties;

    var name = layer.feature.properties.name;

    var ls = M.d_ls[name];

    if(layer.selected) {

      layer.setStyle({

        color: ls.color,
        fillColor: ls.color

      });

      layer.selected=false;
      $select.find("option[value=" + fp.id_area + "]").prop("selected", false);

    }

    else {

      layer.setStyle({

        color: M.color.selected,
        fillColor: M.color.selected

      });

      if( ! $select.prop("multiple") ) {

        $select.find("option:selected").prop("selected", false);

        get_layer_selected(map).forEach(function(_layer){

          _layer.setStyle({

            color: ls.color,
            fillColor: ls.color

          });

          _layer.selected=false;

        });

      }

      layer.selected=true;

      $select.find("option[value=" + fp.id_area + "]").prop("selected", true);

    }

    var data_type_2 = ""
    var val = null;
    var form_name;

    if( M.type_codes_areas_foret.indexOf(map.map_name)>= 0 ) {

      form_name = "form_areas_foret"
      data_type_2 ="id_foret";
      val = parseInt($("#form_foret").attr("data-id-foret"));

    }

    if( M.type_codes_areas_localisation.indexOf(map.map_name )>= 0 ) {

      form_name = "form_areas_localisation";
      data_type_2 ="id_declaration";
      val = parseInt($("#form_declaration").attr("data-id-declaration"));

    }

    M.set_areas_cor(form_name, name, $select.val(), data_type_2, val);

    if(form_name == "form_areas_foret" && M["form_areas_foret"].b_loaded) {

      $("#form_areas_localisation").attr("data-areas", "[]");

    }

  };


  var f_label = function(ls, fp) {

    var s_label = "<h3>" + ls.label + "</h3>";
    s_label+= "<table>";
    s_label+= "<tr>";

    ls.keys.forEach(function(elt){

      s_label+= "<th>" + elt + "</th>";

    });

    s_label+= "</tr>";
    s_label+= "<tr>";

    ls.keys.forEach(function(elt){

      s_label+= "<td>" + fp[elt] + "</td>";

    });

    s_label+= "</tr>";
    s_label+= "</table>";

    return s_label;

  };

  var remove_all  = function(name, map) {

    var $div = $('#' + name);
    var $select_layer = $('#' + map.map_name);
    var $legend = $('#legend-' + name);
    var feature_collection;

    if(M.d_ls[name]) {

      feature_collection = M.d_ls[name].featuresCollection;

    }

    $select_layer.html('<option value=""></option>');

    $legend.hide();
    $div.hide();

    if(feature_collection) {

      feature_collection.eachLayer( function(layer) {

        feature_collection.removeLayer(layer);

      });

    }

  };


  var f_on_data_loaded = function(feature_collection, map, b_zoom) {

    var key_0 = Object.keys(feature_collection._layers)[0];
    var name = feature_collection._layers[key_0].feature.properties.name;

    var $select_layer = $("#" + map.map_name);

    if($select_layer.val()) {

      $select_layer.val("");

    }

    $("#select_map_" + map.map_name + " #chargement").hide();

    var ls = M.d_ls[name];
    if(ls.featuresCollection && b_zoom) {

      deferred_setBounds(ls.featuresCollection.getBounds(), map);

    }

    // selection et affichage
    var form_id = $select_layer.parents("form").attr("id");
    var areas = M.get_areas_cor(form_id, name);

    for(var i=0; i < areas.length; i++) {

      var l = get_layer(map, 'id_area', areas[i].id_area);

      if(l) {

        f_select_layer(l, map);

      }

    }

    var selected = $select_layer.val();

    if(name == "OEASC_ONF_PRF") {

      var opts_list = $select_layer.find('option');

      opts_list.sort(function(a, b) {

        if ( a.value == "" ) return 1;
        if ( b.value == "" ) return -1;

        var s_a = $(a).html().trim();
        var s_b = $(b).html().trim();

        var i_a = parseInt(s_a.split('-')[0]);
        var i_b = parseInt(s_b.split('-')[0]);

        return i_a > i_b ? 1 : -1;

      });

      $select_layer.html('').append(opts_list);
      $select_layer.val(selected);

    }

    // $select_layer.selectpicker("refresh");
    $select_layer.selectpicker();

    $select_layer.change(f_change(map));

    // if( $('#id_form').attr('data-id-form') != "all" ) {

      // $select_layer.selectpicker('toggle');

    // }

    //bidouille bug incompréhensible
    if( selected &&  $select_layer.val()=="" ) {
      $select_layer.val(selected);
      // $select_layer.selectpicker("refresh");
      $select_layer.selectpicker();
    }

    M[form_id].b_loaded=true;

    console.log("Map : " +String(Object.keys(feature_collection._layers).length) + " elements chargés pour " + name + " selected : " + $select_layer.val());

  };


  var f_add_feature_collection_to_map = function(map, name, b_zoom, areas_container=null) {

    var d_ls = M.d_ls;

    $("#select_map_" + map.map_name + " #chargement").show();
    $("#legend-" + name).show();
    $('#' + name).show();

    var ls = d_ls[name];

    var url_base = "/api/ref_geo/areas_from_type_code/";
    var url= "l/";
    url+= name;

    if(areas_container) {

      var i;
      var v=[];
      for(i=0;i<areas_container.length; i++) {

        v.push(areas_container[i].id_area)
      }

      url_base = "/api/ref_geo/areas_from_type_code_container/";
      url += "/" + v.join("-");
    }

    url = url_base + url
    // requete ajax des aires

    var featuresCollection = new L.GeoJSON.AJAX(
      url, {

        pane : 'PANE_' + ls.pane,
        onEachFeature: f_layer(name, d_ls, map),

      });


    // si des objects ont deja été ajoutés avant ou ajoute les nouveaux aux anciens

    if(ls.featuresCollection) {

      featuresCollection.on('data:loaded', function() {

        featuresCollection.eachLayer(function(l) {

          ls.featuresCollection.addLayer(l);

        });

        f_on_data_loaded(this, map, b_zoom);

      });

    }

    // sinon on ajoute les nouveaux à la carte

    else {

      ls.featuresCollection=featuresCollection;

      ls.featuresCollection.addTo(map);

      ls.featuresCollection.on('data:loaded', function() {

        f_on_data_loaded(this, map, b_zoom);

      });

    }

  };


  // recupere tous les layers selectionnne (en orange sur la carte)

  var get_layer_selected = function(map){

    M.l=null;

    var v_l_searched = [];

    map.eachLayer(function(l) {

      if(l.feature) {

        if(l.selected) {

          v_l_searched.push(l);

        }

      }

    });

    return v_l_searched;

  };


  // recupere le (premier) layer ayant l.feature.properties[key]==value

  var get_layer = function(map, key, value){

    M.l=null;

    var l_searched=null;

    if (!value || !key) {

      return null;

    }

    map.eachLayer(function(l) {

      if(l.feature) {

        if(l.feature.properties[key]) {

          if( l.feature.properties[key].toString().trim() == value.toString().trim() ) {

            l_searched = l;

            return;

          }

        }

      }

    });

    return l_searched;

  };


  var carte_base_oeasc = function(name, b_zoom_perimetre=true, tile="mapbox") {

    var map_id = 'map_' + name;

    var map = L.map(map_id, {zoomSnap: 0.1}).setView([44.33, 3.55], 10);
    map.id = map_id;

    $("#" + map.id).parent().find("#chargement").appendTo("#" + map_id);

    if(tile == "mapbox") {

      L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {

        maxZoom: 18,
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox.streets'

      }).addTo(map);

    }

    else if(tile == "opentopomap") {

      L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        maxZoom: 16,
        opacity: 0.6,
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'map style © <a href="https://opentopomap.org/">OpenTopoMap</a>',
        id: 'mapbox.streets'
      }).addTo(map);

    }

    // M.stripes.addTo(map);

    for(var i=0; i < 10; i++) {

      map.createPane('PANE_' + i);
      map.getPane('PANE_' + i).style.zIndex = 1000 + i;

    }

    L.control.betterscale({imperial: false, metric: true}).addTo(map);
    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

      var div=L.DomUtil.create('div','legend');
      // div.innerHTML +='<div id="legend-oeasc"><i style="background: repeating-linear-gradient(45deg, ' + M.color.oeasc + ', ' + M.color.oeasc + ' 2px, white 2px, white 5px); border: 2px solid black;"></i> ' +"OEASC" + '</div>';
      div.innerHTML +='<div id="legend-oeasc"><i style="border: 2px solid black;"></i> ' + "Périmètre de l'OEASC" + '</div>';
      return div;

    };

    legend.addTo(map);

    var l_perimetre_OEASC = new L.GeoJSON.AJAX('/api/ref_geo/areas_from_type_code/l/OEASC_PERIMETRE', {style: M.style.oeasc, pane: 'PANE_0'}).addTo(map);

    if(b_zoom_perimetre) {

      l_perimetre_OEASC.on("data:loaded", function(){ map.fitBounds(this.getBounds());});

    }

    M.l_perimetre_OEASC = l_perimetre_OEASC;



    return map;

  };


  var load_areas = function(areas, type, map, b_zoom) {

    if(areas == []) return ;


    $("#" + map.map_name + " #chargement").show();

    var pane, color;

    pane = (type=="foret")? 1 : 2;
    color = M.color[type];

    $.ajax({

      type: "POST",
      url: "/api/ref_geo/areas_post/l",
      contentType:"application/json; charset=utf-8",
      dataType:"json",
      data: JSON.stringify({areas: areas}),
      success: function (response) {

        console.log("map.map_name", map.map_name);

        var featuresCollection = L.geoJson(response, {
          pane : 'PANE_' + pane
        }).addTo(map);

        featuresCollection.addTo(map);

        featuresCollection.eachLayer(function(layer) {

          layer.setStyle(M.style.default);

          layer.setStyle({

            color: color,
            fillColor: color

          });

          var fp = layer.feature.properties;

          $("#" + map.map_name + " #infos_" + type).append("<div>" + fp.area_name + "</div>")

        });

        $("#" + map.map_name + " #chargement").hide();

        if(type == "foret" && b_zoom) {

          deferred_setBounds(featuresCollection.getBounds(), map);

        }

      }

    });

  };

  var load_declaration_centroid = function(declaration, b_cluster, map) {


    var type = 'localisation';
    var pane, color;
    pane = (type == "foret")? 1 : 2;
    color = M.color[type];

    var areas = declaration.areas_localisation;

    if(areas.length == 0) return ;

    $("#" + map.map_name + " #chargement").show();

    if(!M.markers && b_cluster) {

      M.markers = L.markerClusterGroup();
      map.addLayer(M.markers);

    }


    $.ajax({

      type: "POST",
      url: "/api/ref_geo/areas_centroid_post/l",
      contentType:"application/json; charset=utf-8",
      dataType:"json",
      data: JSON.stringify({areas: areas}),
      success: function (response) {

        var s_popup = '<div><a href="/oeasc/declaration/' + declaration.id_declaration + '"  target="_blank">Alerte ' + declaration.id_declaration + ' </a></div>';

        // s_popup  += '<div><i>Nom forêt</i> : ' + declaration.foret.nom_foret + '</div>';
        // s_popup  += '<div><i>Essence Principale</i> : ' + M.get_db('nomenclature', 'id_nomenclature', declaration.id_nomenclature_peuplement_essence_principale).label_fr + "</div>";

        // s_popup += '<div><i>Dégats</i> : ';

        // for(var i=0; i<declaration.degats.length; i++) {

        //   var degat = M.get_db('nomenclature', 'id_nomenclature', declaration.degats[i].id_nomenclature_degat_type).label_fr;
        //   s_popup += degat;

        //   if(i==declaration.degats.length - 1)

        //     s_popup += '.';

        //   else

        //     s_popup += ',';

        // }

        // s_popup += '</div>';

        var marker = L.marker(response, { pane: 'PANE_' + pane }).bindPopup(s_popup, {opacity: 1, pane: 'PANE_' + M.style.pane.tooltips})

        marker.id_declaration = declaration.id_declaration;

        if(b_cluster) {

          M.markers.addLayer(marker);

        } else {

          map.addLayer(marker);

        }

        marker.on("click", function() {

          $(document).trigger("marker_click", [this.id_declaration]);

        });

        $("#" + map.map_name + " #chargement").hide();

      }

    });

  };
  // on place les fonctions et objets dans M pour les exporter

  M.carte_base_oeasc = carte_base_oeasc;
  M.f_add_feature_collection_to_map =f_add_feature_collection_to_map;
  M.f_select = f_select;
  M.f_select_layer = f_select_layer;
  M.get_layer = get_layer;
  M.remove_all =remove_all;
  M.load_areas = load_areas;
  M.load_declaration_centroid = load_declaration_centroid;

});
