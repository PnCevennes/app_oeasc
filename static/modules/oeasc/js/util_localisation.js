$(document).ready(function() {

  "use strict";

  var initialiser_form_localisation = function(select_name) {

    var map=M["map_" + select_name]

    //reset

    if(map) {

      map.eachLayer(function(l) {

        map.remove(l);
      });

      // $("#map_" + select_name).remove();
      // $("#form_localisation_map_" + select_name).append('<div id="map_' + select_name + '"></div>');

    }

    map = M.carte_base_oeasc(select_name, "opentopomap");

    map.select_name = select_name;

    M["map_" + select_name] = map;

    // modification du style pour le perimetre oeasc

    M.style.oeasc.fillPattern=null;
    M.style.oeasc.fillOpacity=0.1;
    M.l_perimetre_OEASC.setStyle(M.style.oeasc);
     $('#form_' + select_name).find("#legend-oeasc i").css("background", "");


    // initialisation des legendes et select pour la localisation

    M.list.data.forEach(function(name) {

      var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + M.d_ls[name].label + '</div>';
       $('#form_' + select_name).find(".legend").append(s_legend);

    });

    // légende selection

    name="LOCALISATION_SELECTION";
    var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + "Selection" + '</div>';
     $('#form_' + select_name).find(".legend").append(s_legend);

    // on cache ttes les légendes

    M.list.data.forEach(function(e) {

       $('#form_' + select_name).find("#legend-" + e).hide();

    });

     $('#form_' + select_name).find('#chargement').hide();



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

    $("#form_" + map.select_name + " .localisation-select").on("mouseover", "ul.inner > li", f_option_hover(map));
    $("#form_" + map.select_name + " .localisation-select").on("mouseout", "ul.inner > li", f_option_hover(map));

    var localisation_type = $("#form_" + select_name).attr("data-localisation-type");

    var areas_container = JSON.parse($("#form_" + select_name).attr("data-areas-container").replace(/\'/g, '"').replace(/None/g, 'null'));

    if(localisation_type == "COMMUNE") {

      name = 'OEASC_COMMUNE';
      M.f_add_feature_collection_to_map(map, name);

    }

    if(localisation_type == "ONF_FRT") {

      name = 'OEASC_ONF_FRT';
      M.f_add_feature_collection_to_map(map, name);

    }

    if(localisation_type == "DGD") {

      name = 'OEASC_DGD';
      M.f_add_feature_collection_to_map(map, name);

    }

    if(localisation_type == "ONF_PRF") {

      for (var i =0; i<areas_container.length; i++) {

        name = 'OEASC_ONF_PRF';

        var area_code = M.get_db('t_areas','id_area',areas_container[i].id_area).area_code

        var fp = {
          name: 'OEASC_ONF_FRT',
          area_code: area_code,
        };

        M.f_add_feature_collection_to_map(map, name, fp);

      }

    }

  };

  M.initialiser_form_localisation = initialiser_form_localisation;

});
