$(document).ready(function() {

  "use strict";


  var init_map = function(map_name) {

    var map=M["map_" + map_name]

    //reset

    if(map) {

      map.eachLayer(function(l) {

        map.remove(l);

      });

    }

    map = M.carte_base_oeasc(map_name, "mapbox");

    map.map_name = map_name;

    M["map_" + map_name] = map;

    M.style.oeasc.fillPattern = null;
    M.style.oeasc.fillOpacity = 0.1;
    M.l_perimetre_OEASC.setStyle(M.style.oeasc);
    $('#' + map_name).find("#legend-oeasc i").css("background", "");

    return map;

  };


  var initialiser_show_declarations = function(map_name, declarations) {

    var map = init_map(map_name);

    declarations.forEach(function(e) {

      M.load_declaration_centroid(e , true, map);

    });

  };


  var initialiser_show_localisation = function(map_name, declaration) {

    var map = init_map(map_name);

    var name = 'foret';
    var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + "Foret" + '</div>';
    $('#' + map_name).find(".legend").append(s_legend);

    name = 'localisation';
    var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + "Parcelle" + '</div>';
    $('#' + map_name).find(".legend").append(s_legend);


    // charger les foret

    var areas_foret = declaration.foret.areas_foret;

    M.load_areas(areas_foret, "foret", map);


    // charger les aires

    var areas_localisation = declaration.areas_localisation;

    M.load_areas(areas_localisation, "localisation", map);

    M.load_declaration_centroid(declaration, false, map);

  };


  var initialiser_form_localisation = function(id_form) {

    $('#' + id_form + ' .select_map').each(function() {

      M[id_form] = {}
      M[id_form].b_loaded = false;


      var type_code = $(this).attr("data-type-code");

      if(type_code) {

        initialiser_select_map(type_code);

      }

    });

  }


  var initialiser_select_map = function(map_name) {

    var map = init_map(map_name);

    // initialisation des legendes et select pour la localisation

    M.list.data.forEach(function(name) {

      var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + M.d_ls[name].label + '</div>';
      $('#select_map_' + map_name).find(".legend").append(s_legend);

    });

    // légende selection

    name="LOCALISATION_SELECTION";
    var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + "Selection" + '</div>';
    $('#select_map_' + map_name).find(".legend").append(s_legend);

    // on cache ttes les légendes

    M.list.data.forEach(function(e) {

     $('#select_map_' + map_name).find("#legend-" + e).hide();

   });

    $('#select_map_' + map_name).find('#chargement').hide();

    $('#' + name).parent().find('.bs-select-all').click( function() {

      $('#' + name).change();

    });

    // les tooltip des layer s'affichent au survol des options

    var f_option_hover = function(map) {
      return function(e) {

        var $this = $(this);

        var area_name = $this.find('.text').html().trim();

        var l = M.get_layer(map, "area_name", area_name);

        if( l ) {

          l.fire(e.type);
        }

      };

    };

    $("#select_map_" + map.map_name + " .localisation-select").on("mouseover", "ul.inner > li", f_option_hover(map));
    $("#select_map_" + map.map_name + " .localisation-select").on("mouseout", "ul.inner > li", f_option_hover(map));

    var type_code = $("#select_map_" + map_name).attr("data-type-code");
    var areas_container = JSON.parse($("#select_map_" + map_name).attr("data-areas-container"));

    if(areas_container.length > 0) {

      for (var i=0; i<areas_container.length; i++) {

       M.f_add_feature_collection_to_map(map, type_code, areas_container[i].id_area);

     }

     M.load_areas(areas_container, 'foret', map);

   } else {

     M.f_add_feature_collection_to_map(map, type_code);

   }

 };

 M.initialiser_form_localisation = initialiser_form_localisation;
 M.initialiser_show_localisation = initialiser_show_localisation;
 M.initialiser_show_declarations =initialiser_show_declarations;

});
