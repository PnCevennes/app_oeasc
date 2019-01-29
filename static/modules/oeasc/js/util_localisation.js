$(document).ready(function() {

  "use strict";

  var initialiser_show_declarations = function(map_name, declarations, config) {

    var map = M.init_map(map_name, config);

    M.load_declarations_centroid(declarations, map, config);

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
      var s_text_legend = M.d_ls[name].label;
      if(['OEASC_ONF_FRT', 'OEASC_DGD'].includes(name)) {
        s_text_legend = "Forêt concernée par l'alerte"
      };
      if(['OEASC_CADASTRE', 'OEASC_ONF_PRF', 'OEASC_ONF_UG'].includes(name)) {
        s_text_legend = "Parcelle concernée par l'alerte"
      }


      var s_legend = '<div id="legend-' + name + '"><i style="background: ' + color + '; border: solid;"></i> ' + s_text_legend + '</div>';
      $('#map_' + map_name).find(".legend").append(s_legend);
    });

    // on cache ttes les légendes
    M.list.data.forEach(function(e) {
      $('#map_' + map_name).find("#legend-" + e).hide();
    });

    // charger les foret
    if (config && config.type && config.type.includes("foret")) {
      b_tooltip = false;
      var zoom = config && config.zoom && config.zoom=="foret";
      var areas_foret = declaration.foret.areas_foret.filter((a) => {return ["OEASC_DGD", "OEASC_ONF_FRT"].includes(a.type_code) });
      if(!areas_foret.length) {
        areas_foret = declaration.foret.areas_foret.filter((a) => {return ["OEASC_SECTION"].includes(a.type_code)});
        b_tooltip=zoom;
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
      declaration.centroid && M.load_declarations_centroid([declaration], map, config);
    }

  };

  M.initialiser_show_localisation = initialiser_show_localisation;
  M.initialiser_show_declarations = initialiser_show_declarations;

});
