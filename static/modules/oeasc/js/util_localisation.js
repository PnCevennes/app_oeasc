$(document).ready(function() {

  "use strict";

  var initialiser_show_declarations = function(map_name, declarations) {

    var map = M.init_map(map_name);

    M.load_declarations_centroid(declarations, map, "Circle", true);

    var s_legend = '<div id="legend-gravite_faible"><i style="color: black;">●</i> Déclarations </div>';
    $('#' + map_name).find(".legend").append(s_legend);

    // var s_legend = '<div id="legend-gravite_faible"><i style="color: yellow;">●</i> Gravité : faible </div>';
    // $('#' + map_name).find(".legend").append(s_legend);

    // var s_legend = '<div id="legend-gravite_modérée"><i style="color: orange;">●</i> Gravité : modérée</div>';
    // $('#' + map_name).find(".legend").append(s_legend);

    // var s_legend = '<div id="legend-gravite_importante"><i style="color: red;">●</i> "Gravité : importante</div>';
    // $('#' + map_name).find(".legend").append(s_legend);

  };


  var initialiser_show_localisation = function(map_name, declaration, config) {

    var map = M.init_map(map_name, config);
    var list_localisation = ["OEASC_CADASTRE", "OEASC_ONF_PRF"];
    var list_foret = ["OEASC_DGD", "OEASC_ONF_FRT", 'OEASC_SECTION'];
    var base_map = (config && config.base_map) || 'Mapbox';

    var titre = $('#' + map.id).attr("titre");
    if(titre) {
      M.add_titre(titre, map);
    }

    map.removeLayer(map.base_maps[map.cur_tile_name]);
    map.addLayer(map.base_maps[base_map]);
    // initialisation des legendes pour tout les type présents dans M.list.data
    M.list.data.forEach(function(name) {
      var color;
      if(list_foret.includes(name)) {
        color = M.color['foret'];
      } else if (list_localisation.includes(name)) {
        color = M.color['localisation'];
      } else {
        return;
      };
      var s_legend = '<div id="legend-' + name + '"><i style="background: ' + color + '; border: solid;"></i> ' + M.d_ls[name].label + '</div>';
      $('#map_' + map_name).find(".legend").append(s_legend);
    });

    // on cache ttes les légendes
    M.list.data.forEach(function(e) {
      $('#map_' + map_name).find("#legend-" + e).hide();
    });

    // charger les secteurs
    if (config && config.type && config.type.includes("secteurs")) {
      M.add_secteurs(map, config && config.zoom && config.zoom=="secteurs");
    }

    // charger les foret
    if (config && config.type && config.type.includes("foret")) {
      b_tooltip = false;
      var zoom = config && config.zoom && config.zoom=="foret";
      var areas_foret = declaration.foret.areas_foret.filter((a) => {return ["OEASC_DGD", "OEASC_ONF_FRT"].includes(a.type_code) });
      if(!areas_foret.length) {
        areas_foret = declaration.foret.areas_foret.filter((a) => {return ["OEASC_SECTION"].includes(a.type_code)});
        b_tooltip=zoom && areas_foret.length > 1;
      }
      M.load_areas(areas_foret, "foret", map, zoom, b_tooltip);
    }

    // charger les aires (parcelles)
    if (config && config.type && config.type.includes("localisation")) {
      var zoom = config && config.zoom && config.zoom=="localisation";
      var areas_localisation = declaration.areas_localisation.filter((a) => {return ["OEASC_CADASTRE", "OEASC_ONF_PRF"].includes(a.type_code) });
      var b_tooltip = config.tooltip && config.tooltip.includes('localisation');
      M.load_areas(areas_localisation, "localisation", map, zoom, b_tooltip);
    }

    // centroid ??
    if (config && config.centroid) {
      declaration.centroid && M.load_declarations_centroid([declaration], map);
    }

  };

  M.initialiser_show_localisation = initialiser_show_localisation;
  M.initialiser_show_declarations = initialiser_show_declarations;

});
