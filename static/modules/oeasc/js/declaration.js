  $(document).ready(function() {

    "use strict";

    var init_maps_declaration = function(id_declaration) {

      var declaration = JSON.parse($('#declaration_' + id_declaration).attr("data-declaration"));

      if(! M["map_show_localisation_" + id_declaration] && declaration) {

        var d_config = {
          'global': {
            'base_map': 'Mapbox',
            'type': ['foret', 'secteurs'],
            'zoom': 'secteurs',
            'centroid': {
              'type': 'marker',
              'global': false,
            },
          },
          'medium': {
            // 'base_map': 'Mapbox',
            'base_map': 'Cartes (IGN)',
            'type': ['foret', 'localisation'],
            'zoom': "foret",
            'centroid': {
              'type': 'marker',
              'global': false,
            },
          },
          'local': {
            'base_map': 'Cartes (IGN)',
            'type': ['localisation'],
            'zoom': "localisation",
            'tooltip': "localisation",
          },
        };
        setTimeout(function() {
          $("#declaration_" + id_declaration + " .localisation-map").each((i, e) => {
            var type_map = $(e).attr("type-map");
            var id = e.id;
            var map_name = id.substr(4);
            M.initialiser_show_localisation(map_name, declaration, d_config[type_map]);
          });
        }, 10);
      }

    }

    M.init_maps_declaration = init_maps_declaration;

  });
