$(document).ready(function() {

  "use strict";

  var initialiser_show_declarations = function(map_name, declarations) {

    var map = M.init_map(map_name);

    M.load_declarations_centroid(declarations, map);

    var s_legend = '<div id="legend-gravite_faible"><i style="color: black;">●</i> Déclarations </div>';
    $('#' + map_name).find(".legend").append(s_legend);

    // var s_legend = '<div id="legend-gravite_faible"><i style="color: yellow;">●</i> Gravité : faible </div>';
    // $('#' + map_name).find(".legend").append(s_legend);

    // var s_legend = '<div id="legend-gravite_modérée"><i style="color: orange;">●</i> Gravité : modérée</div>';
    // $('#' + map_name).find(".legend").append(s_legend);

    // var s_legend = '<div id="legend-gravite_importante"><i style="color: red;">●</i> "Gravité : importante</div>';
    // $('#' + map_name).find(".legend").append(s_legend);

  };


  var initialiser_show_localisation = function(map_name, declaration) {

    var map = M.init_map(map_name);

    var name = 'foret';
    var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + "Foret" + '</div>';
    $('#' + map_name).find(".legend").append(s_legend);

    name = 'localisation';
    var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + "Parcelle" + '</div>';
    $('#' + map_name).find(".legend").append(s_legend);

    // charger les foret

    var areas_foret = declaration.foret.areas_foret.filter((a) => {return ["OEASC_DGD", "OEASC_ONF_FRT"].includes(a.type_code) }) || areas_foret;

    M.load_areas(areas_foret, "foret", map, true);


    // charger les aires

    var areas_localisation = declaration.areas_localisation.filter((a) => {return ["OEASC_CADASTRE", "OEASC_ONF_PRF"].includes(a.type_code) });

    M.load_areas(areas_localisation, "localisation", map, false);

    M.load_declarations_centroid([declaration], map);

  };

  M.initialiser_show_localisation = initialiser_show_localisation;
  M.initialiser_show_declarations = initialiser_show_declarations;

});
