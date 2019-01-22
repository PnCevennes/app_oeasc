/* fonctions de base pour les carte qui vont concerner plusieurs types de carte
par exemple :
  - select_map-select_map,
  - carte de présentation de la zône étudiée
  - carte de visualisation des résultats, etc..
  */

  $(document).ready(function() {

    "use strict";

    var setBounds = function(bounds, map, d=1e3) {
    // redéfini les limites de la carte
    if(bounds.isValid()) {
      var dlat = (bounds._northEast.lat - bounds._southWest.lat) / d;
      var dlon = (bounds._northEast.lon - bounds._southWest.lon) / d;
      bounds._northEast.lat += dlat;
      bounds._northEast.lon += dlon;
      bounds._southWest.lat -= dlat;
      bounds._southWest.lon -= dlon;
      map.fitBounds(bounds);
    }
  };

  var deferred_setBounds = function(bounds, map, d=1e3) {
    // redéfini les limites de la carte (avec un délai pour éviter certains bugs: carte pas encore prête)
    return new Promise((resolve) => {
      setTimeout( setBounds, 500, bounds, map, d);
      resolve();
    });
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
        setTimeout(()=>{
          console.log("done", map.id);
          resolve();
        }, 100);
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

  var carte_base_oeasc = function(name, config=null) {
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
    var div_perimetre = "";
    if(config && config.type && config.type.includes("perimetre")) {
      div_perimetre ='<div id="legend-oeasc"><i style="background: lightgrey;border: 2px solid black;"></i> ' + "Périmètre de l'Observatoire" + '</div>';

      // ajout du périmètre OEASC
      var l_perimetre_OEASC = new L.GeoJSON.AJAX('/api/ref_geo/areas_simples_from_type_code/l/OEASC_PERIMETRE', {
        style: M.style.oeasc,
        pane: 'PANE_1'
      }).addTo(map);
      if(config && config.zoom && config.zoom.includes("perimetre")) {
        l_perimetre_OEASC.on("data:loaded", function(){ map.fitBounds(this.getBounds());});
      }
      l_perimetre_OEASC.setStyle(M.style.oeasc);

    }

    var legend = L.control({position: 'bottomright'});
    legend.onAdd = function (map) {
      var div=L.DomUtil.create('div','legend');
      div.innerHTML += div_perimetre;
      return div;
    };
    legend.addTo(map);

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

  var init_map = function(map_name, config=null) {
    /*  initialise une carte reférencée par map name

    map_name: nom de la carte
    */

    // reset si la carte existe déjà
    remove_map(map_name)

    // creation de la carte
    var map=M["map_" + map_name]
    map = M.carte_base_oeasc(map_name, config);
    map.map_name = map_name;
    M["map_" + map_name] = map;

    // style perimetre oeasc

    return map;

  };


  var add_titre = function(titre, map) {
    $('#' + map.id).append("<div class='map-titre'><div>" + titre + "</div></div>")
  };

  var add_sous_titre = function(sous_titre, map) {
    $('#' + map.id).append("<div class='map-sous-titre'><div>" + sous_titre + "</div></div>")

  };


// return array of [r,g,b,a] from any valid color. if failed returns undefined
var colorValues  = function(color)
{
  if (color === '')
    return;
  if (color.toLowerCase() === 'transparent')
    return [0, 0, 0, 0];
  if (color[0] === '#')
  {
    if (color.length < 7)
    {
            // convert #RGB and #RGBA to #RRGGBB and #RRGGBBAA
            color = '#' + color[1] + color[1] + color[2] + color[2] + color[3] + color[3] + (color.length > 4 ? color[4] + color[4] : '');
          }
          return [parseInt(color.substr(1, 2), 16),
          parseInt(color.substr(3, 2), 16),
          parseInt(color.substr(5, 2), 16),
          color.length > 7 ? parseInt(color.substr(7, 2), 16)/255 : 1];
        }
        if (color.indexOf('rgb') === -1)
        {
        // convert named colors
        var temp_elem = document.body.appendChild(document.createElement('fictum')); // intentionally use unknown tag to lower chances of css rule override with !important
        var flag = 'rgb(1, 2, 3)'; // this flag tested on chrome 59, ff 53, ie9, ie10, ie11, edge 14
        temp_elem.style.color = flag;
        if (temp_elem.style.color !== flag)
            return; // color set failed - some monstrous css rule is probably taking over the color of our object
          temp_elem.style.color = color;
          if (temp_elem.style.color === flag || temp_elem.style.color === '')
            return; // color parse failed
          color = getComputedStyle(temp_elem).color;
          document.body.removeChild(temp_elem);
        }
        if (color.indexOf('rgb') === 0)
        {
          if (color.indexOf('rgba') === -1)
            color += ',1'; // convert 'rgb(R,G,B)' to 'rgb(R,G,B)A' which looks awful but will pass the regxep below
          return color.match(/[\.\d]+/g).map(function (a)
          {
            return +a
          });
        }
      }

////////////////////////////////////////////////////////////
var load_areas = function(areas, type, map, b_zoom, b_tooltip=false) {
    /*
      charge les aires dont l'id est contenu dans area
      */
      if(areas == []) return ;

      $("#" + map.map_name + " #chargement").show();

      var pane = (type=="foret")? 2 : 3;
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
                direction: 'center',
                color: 'white',
                opacity: 1,
                fillOpacity: 1,
                className: 'tooltip-' + type,
              });
              // legende
              var cv = colorValues(color).map((a)=>{return "" + a})
              cv[3] = '0.5';
              $("#map_" + map.map_name + ' #legend-' + type_code).show();
              $("#map_" + map.map_name + ' #legend-' + type_code + ' > i').css('background-color', 'rgba(' + cv.join(",") + ')');
              $("#map_" + map.map_name + ' #legend-' + type_code + ' > i').css('border-color', color);
              $("#map_" + map.map_name + ' #legend-' + type_code + ' > i').css('border-width', weight);

              if(b_zoom) v_sous_titre.push(fp.label);
            });



          // chargement
          $("#" + map.map_name + " #chargement").hide();

          if(b_zoom) {
            v_sous_titre && add_sous_titre(v_sous_titre.join(', '), map);
            deferred_setBounds(featuresCollection.getBounds(), map, 5)
            .then(() => {
              setTimeout(()=>{
                var z = map.getZoom();
                console.log(map.id, type, z);
                if(z > 15) {
                  map.setZoom(15);
                };
                resolve();
              }, 500)
            });
          }
          else {
            resolve();
          }
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
          layer.setStyle({
            fillColor: color_secteur[feature.properties.area_code],
            color: 'grey',
            weight : 2,
            fillOpacity :0.1,
            opacity :1,
          });
          layer.bindTooltip(feature.properties.label, {
            pane: 'PANE_4',
            permanent: true,
            // direction: 'center',
            direction: 'center',
            color: color_secteur[feature.properties.area_code],
            opacity: 0.8,
            fillOpacity: 1,
            weight: 3,
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

    $(".legend").append('<div id="#legend-zc"><i style="background-color: rgb(184, 206, 145); border: 2px solid grey;"></i> ' +"<b>Secteurs d'étude</b>" + '</div>');

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
