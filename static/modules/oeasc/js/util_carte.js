/* fonctions de base pour les carte qui vont concerner plusieurs types de carte
par exemple :
  - select_map-select_map,
  - carte de présentation de la zône étudiée
  - carte de visualisation des résultats, etc..
  */

  $(document).ready(function() {

    "use strict";

    var setBounds = function(bounds, map) {
    // redéfini les limites de la carte
    if(bounds.isValid()) {
      map.fitBounds(bounds);
    }
  };

  var deferred_setBounds = function(bounds, map) {
    // redéfini les limites de la carte (avec un délai pour éviter certains bugs: carte pas encore prête)
    setTimeout( setBounds, 500, bounds, map);
  };


  var get_layer = function(map, key, value){
    // recupere le (premier) layer ayant l.feature.properties[key]==value
    //
    // key : nom du champs pour un élément du dict. l.feature.properties
    // value : on cherche l'élément tq. l.feature.properties[key] == value

    if (!value || !key) {
      return null;
    }

    var l_searched = null;

    map.eachLayer(function(l) {
      if( ! l.feature ) {
        return;
      }
      if( ! l.feature.properties[key] ){
        return;
      }
      if( l.feature.properties[key].toString().trim() == value.toString().trim() ){
        l_searched = l;
      }
      return;
    });

    return l_searched;
  };

  var init_tiles = function(map) {
    // initialise les fonds de carte

    // openstreetmap
    var tile_opacity = 0.7;
    var mapbox = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
      maxZoom: 18,
      opacity: tile_opacity,
      // attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
      // '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      // 'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
      id: 'mapbox.streets'
    })

    //ign cartes
    var key = 'choisirgeoportail';
    var s_layer = 'GEOGRAPHICALGRIDSYSTEMS.MAPS';
    var ign = L.tileLayer("http://wxs.ign.fr/" + key
      + "/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&"
      + "LAYER=" + s_layer + "&STYLE=normal&TILEMATRIXSET=PM&"
      + "TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image%2Fjpeg", {
        opacity: tile_opacity,
        maxZoom: 18,
        id: 'mapbox.streets',
        attribution: '&copy; <a href="http://www.ign.fr/">IGN</a>'
      });

    // ign ortho
    var s_layer = 'ORTHOIMAGERY.ORTHOPHOTOS';
    var ign_ortho = L.tileLayer("http://wxs.ign.fr/" + key
      + "/geoportail/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&"
      + "LAYER=" + s_layer + "&STYLE=normal&TILEMATRIXSET=PM&"
      + "TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image%2Fjpeg", {
        opacity: tile_opacity,
        maxZoom: 18,
        id: 'mapbox.streets',
        attribution: '&copy; <a href="http://www.ign.fr/">IGN</a>'
      });

    var base_maps = {
      "Mapbox": mapbox,
      "Cartes (IGN)": ign,
      "Vue aérienne (IGN)": ign_ortho
    };

    if(! map.cur_tile_name ){
      map.cur_tile_name = "Mapbox";
    }

    return base_maps;
  }

  var wait_for_map_loaded = function(map) {
    return new Promise((resolve) => {
      Promise.all(map.promises).then(()=>{
        console.log("wait 2s", map.id);
        setTimeout(()=>{
          console.log("done", map.id);
          resolve();
        }, 2000);
        return true;
      });
    });
  };

  var remove_promise_on_tile = function(map) {
    var p_tile = map.promises.find((e)=>{return e.type == "tile"})
    p_tile && map.promises.splice(map.promises.indexOf(p_tile), 1);
  }

  var add_promise_on_tile = function(map) {
    map.base_maps[map.cur_tile_name].on('tileload', (e) => {
      var p = new Promise((resolve)=>{
        map.base_maps[map.cur_tile_name].on('load', function(e) {
          resolve();
        });
      });
      p.type="tile";
      map.promises.push(p);
    });
  };

  var carte_base_oeasc = function(name, b_zoom_perimetre=true) {
    // carte de base commune à toutes les cartes
    //
    // name: nom de la carte
    // b_zoom_perimetre: zoomer sur le perimetre de l'OEASC à la fin de l'initialisation

    var map_id = 'map_' + name;
    var L_PREFER_CANVAS = true;
    var map = L.map(map_id, {
      zoomSnap: 0.1,
      // preferCanvas:true,
    }).setView([44.33, 3.55], 10);
    map.promises=[1];
    map.id = map_id;

    // ajout du cadre "chargement"
    $("#" + map.id).parent().find("#chargement").appendTo("#" + map_id).hide();

    // initialisation des fonds de carte (on garde en mémoire le dernier choisi)
    map.base_maps = init_tiles(map);
    map.on('baselayerchange', function(e) {
      map.cur_tile_name=e.name;
      remove_promise_on_tile(map);
      add_promise_on_tile(map)
    });

    map.base_maps[map.cur_tile_name].addTo(map);
    add_promise_on_tile(map)



    map.layerControl = L.control.layers(map.base_maps).addTo(map);

    map.on('resize', function(e) {
      add_promise_on_tile(map)
    });


    // creation de pane
    for(var i=0; i < 10; i++) {
      map.createPane('PANE_' + i);
      map.getPane('PANE_' + i).style.zIndex = 1000 + i;
    }

    L.control.betterscale({imperial: false, metric: true}).addTo(map);
    // ajout de l'échelle
    setTimeout(function() {
     var b=map.getBounds()
     b._northEast.lat+=0.001;
     map.fitBounds(b);
   }, 1);

    // ajout de la légende
    var legend = L.control({position: 'bottomright'});
    legend.onAdd = function (map) {
      var div=L.DomUtil.create('div','legend');
      div.innerHTML +='<div id="legend-oeasc"><i style="background: lightgrey;border: 2px solid black;"></i> ' + "Périmètre de l'Observatoire" + '</div>';
      return div;
    };
    legend.addTo(map);

    // ajout du périmètre OEASC
    var l_perimetre_OEASC = new L.GeoJSON.AJAX('/api/ref_geo/areas_simples_from_type_code/l/OEASC_PERIMETRE', {
      style: M.style.oeasc,
      pane: 'PANE_1'
    }).addTo(map);
    if(b_zoom_perimetre) {
      l_perimetre_OEASC.on("data:loaded", function(){ map.fitBounds(this.getBounds());});
    }
    map.l_perimetre_OEASC = l_perimetre_OEASC;


    return map;

  };

  var remove_map = function(map_name) {
    /*  efface toutes les layers d'une carte

    map_name: nom de la carte
    */

    var map=M["map_" + map_name]
    if(map) {
      map.eachLayer(function(l) {
        map.remove(l);
      });
    }

    delete M["map_" + map_name];
  }

  var init_map = function(map_name) {
    /*  initialise une carte reférencée par map name

    map_name: nom de la carte
    */

    // reset si la carte existe déjà
    remove_map(map_name)

    // creation de la carte
    var map=M["map_" + map_name]
    map = M.carte_base_oeasc(map_name, false);
    map.map_name = map_name;
    M["map_" + map_name] = map;

    // style perimetre oeasc
    map.l_perimetre_OEASC.setStyle(M.style.oeasc);

    return map;

  };


  var add_titre = function(titre, map) {
    $('#' + map.id).append("<div class='map-titre'><div>" + titre + "</div></div>")
  };

  var add_sous_titre = function(sous_titre, map) {
    $('#' + map.id).append("<div class='map-sous-titre'><div>" + sous_titre + "</div></div>")

  };

////////////////////////////////////////////////////////////
var load_areas = function(areas, type, map, b_zoom, b_tooltip=false) {
    /*
      charge les aires dont l'id est contenu dans area
      */
      if(areas == []) return ;

      $("#" + map.map_name + " #chargement").show();

      var pane = (type=="foret")? 1 : 2;
      var color = M.color[type];


      $("#map_" + map.map_name + ' #legend-' + name).show()
      map.promises.push(new Promise((resolve) => {
        $.ajax({

          type: "POST",
          url: "/api/ref_geo/areas_post/l",
          contentType:"application/json; charset=utf-8",
          dataType:"json",
          data: JSON.stringify({areas: areas}),
          success: function (response) {

            var featuresCollection = L.geoJson(response, {
              pane : 'PANE_' + pane
            }).addTo(map);

            var v_sous_titre=[];
            var weight = b_zoom ? 3 : 2;
            featuresCollection.eachLayer(function(layer) {
              var fp = layer.feature.properties;
              var type_code = M.get_type_code(fp.id_type);
              layer.setStyle(M.style.default);
              layer.setStyle({
                color: color,
                fillColor: color,
                weight: weight,
              });
              b_tooltip && layer.bindTooltip(fp.label, {
                pane: 'PANE_4',
                permanent: true,
                direction: 'auto',
                color: 'white',
                opacity: 1,
                fillOpacity: 1,
                className: '',
              });
              // legende
              $("#map_" + map.map_name + ' #legend-' + type_code).show();
              $("#map_" + map.map_name + ' #legend-' + type_code + ' > i').css('background-color', color);

              if(b_zoom) v_sous_titre.push(fp.label);
            });



          // chargement
          $("#" + map.map_name + " #chargement").hide();

          if(b_zoom) {
            v_sous_titre && add_sous_titre(v_sous_titre.join(', '), map);
            deferred_setBounds(featuresCollection.getBounds(), map);
          }
          resolve();
        }
      })
      }));
    };


    var load_declarations_centroid = function(declarations, map, type="marker", b_global = false) {
    /* charge les centroids des déclarations
    */
    var d_areas = {};
    var d_deg_color = {};

    if( ! map.markers && b_global) {
      map.markers = L.layerGroup();
      map.addLayer(map.markers);
      map.layerControl.addOverlay(map.markers, "Déclarations")
    }
    var k;
    for(k=0; k < declarations.length; k++) {

      var declaration = declarations[k];
      var id_declaration = declaration.id_declaration;
      var s_popup = '<div><a href="/declaration/declaration/' + id_declaration + '"  target="_blank">Alerte ' + id_declaration + ' </a></div>';
      var centroid = declaration.centroid;
      var marker;
      if(type == "circle") {
        marker = L.circle(centroid);
      } else {
        marker = L.marker(centroid);
      }
      L.setOptions(marker, { color: "black", radius: 100, pane: 'PANE_5'});
      marker.bindPopup(s_popup, {opacity: 1, pane: 'PANE_6'});
      marker.id_declaration = id_declaration;
      if(b_global) {
        map.markers.addLayer(marker);
      } else {
        map.addLayer(marker);
      }
      marker.on("click", function() {
        $(document).trigger("marker_click", [this.id_declaration]);
      });
    }
  };

  // ajout des secteurs
  var add_secteurs = function(map, b_zoom=false) {
    var color_secteur = {
      'Causses et Gorges': 'red',
      'Aigoual': 'blue',
      'Mont Lozère': 'green',
      'Vallées cévenoles': 'purple'
    }
    var l_secteurs_OEASC = new L.GeoJSON.AJAX(
      '/api/ref_geo/areas_simples_from_type_code/l/OEASC_SECTEUR', {
        style: M.style.secteur,
        pane: 'PANE_1',
        onEachFeature: function(feature, layer) {
          var center = layer.getBounds().getCenter();
          layer.bindTooltip(feature.properties.label, {
            pane: 'PANE_4',
            permanent: true,
            // direction: 'center',
            direction: 'center',
            color: color_secteur[feature.properties.area_code],
            opacity: 1,
            fillOpacity: 1,
            className: 'secteur ' + feature.properties.area_code.replace(/ /g, "_"),
          });
        },
      }
      ).addTo(map);

    l_secteurs_OEASC.on('data:loaded', function() {
      if(b_zoom) {
        deferred_setBounds(l_secteurs_OEASC.getBounds(), map);
      }
    });

    $(".legend").append('<div id="#legend-zc"><i style="background: lightgrey; border: 1px solid black;"></i> ' +"<b>Secteurs d'étude</b>" + '</div>');

  }


  // on place les fonctions et objets dans M pour les exporter

  M.carte_base_oeasc = carte_base_oeasc;
  M.get_layer = get_layer;
  M.load_areas = load_areas;
  M.add_secteurs = add_secteurs;
  M.load_declarations_centroid = load_declarations_centroid;
  M.remove_map = remove_map;
  M.init_map = init_map;
  M.deferred_setBounds = deferred_setBounds;
  M.add_titre = add_titre;
  M.add_sous_titre = add_sous_titre;
  M.wait_for_map_loaded = wait_for_map_loaded;

});
