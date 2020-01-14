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
    var ign = L.tileLayer("https://wxs.ign.fr/" + key
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
    var ign_ortho = L.tileLayer("https://wxs.ign.fr/" + key
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
          map.promises = map.promises.filter((p) => {
            return !p.resolved;
          });
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
      // map.on('loading', (e) => {
        var p = new Promise((resolve)=>{
          map.base_maps[map.cur_tile_name].on('load', function(e) {
          // map.on('load', function(e) {
            resolve(2);
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


    // titre
    var titre = $('#' + map.id).attr("titre");
    if(titre) {
      M.add_titre(titre, map);
    }

    // initialisation des fonds de carte (on garde en mémoire le dernier choisi)
    map.base_maps = init_tiles(map);
    map.on('baselayerchange', function(e) {
      map.cur_tile_name=e.name;
      remove_promise_on_tile(map);
      add_promise_on_tile(map)
    });

    map.cur_tile_name = (config && config.base_map) || 'Mapbox';

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
      div.innerHTML += "";
      return div;
    };
    legend.addTo(map);


    // ajout du périmètre OEASC
    if(config && config.type && config.type.includes("perimetre")) {
      var div_perimetre ='<div id="legend-oeasc"><i style="background: lightgrey;border: 2px solid black;"></i> ' + "Périmètre de l'Observatoire" + '</div>';

      var l_perimetre_OEASC = new L.GeoJSON.AJAX('/api/ref_geo/areas_simples_from_type_code/l/OEASC_PERIMETRE', {
        style: M.style.oeasc,
        pane: 'PANE_1'
      }).addTo(map);
      if(config && config.zoom && config.zoom.includes("perimetre")) {
        l_perimetre_OEASC.on("data:loaded", function(){ map.fitBounds(this.getBounds());});
      }
      l_perimetre_OEASC.setStyle(M.style.oeasc);
      $("#" + map.id + " .legend").append(div_perimetre);

    }


    // secteurs
    if (config && config.type && config.type.includes("secteurs")) {
      M.add_secteurs(map, config && config.zoom && config.zoom=="secteurs");
    }

    if (config && config.type && config.type.includes("zc")) {
      var l_zone_coeur = new L.GeoJSON.AJAX('/api/ref_geo/areas_simples_from_type_code/l/ZC_PNC', {
        pane: 'PANE_0',
        style: M.style.zc
      }).addTo(map);
      $("#" + map.id + " .legend").append('<div id="#legend-aa"><i style="background: ' + M.color.zc + '; border: 1px solid darkgrey;"></i> ' +"Zone cœur du Parc national" + '</div>');
    }
    if (config && config.type && config.type.includes("aa")) {
      var l_Aire_Adhesion = new L.GeoJSON.AJAX('/api/ref_geo/areas_simples_from_type_code/l/AA_PNC', {
        pane: 'PANE_0',
        style: M.style.aa,
      }).addTo(map);
      $("#" + map.id + " .legend").append('<div id="#legend-zc"><i style="background: ' + M.color.aa + '; border: 1px solid darkgrey;"></i> ' +"Aire d'adhésion du Parc national" + '</div>');
    }


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
    $('#' + map.id).parent().prepend("<div class='map-titre'><div>" + titre + "</div></div>")
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
      if(!(areas && areas.length)) return ;

      $("#" + map.map_name + " #chargement").show();

      var pane = (type=="foret")? 2 : 3;
      var color = M.color[type];

      var p = new Promise((resolve) => {

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
              var s_tooltip = fp.label;
              if(type_code == 'OEASC_CADASTRE') {
                s_tooltip = s_tooltip.split('-')[2]
              }
              b_tooltip && layer.bindTooltip(s_tooltip, {
                pane: 'PANE_4',
                permanent: true,
                direction: 'center',
                color: 'white',
                opacity: 1,
                fillOpacity: 1,
                className: ' tooltip tooltip-' + type,
              });

              // legende
              var cv = colorValues(color).map((a)=>{return "" + a})
              cv[3] = '0.5';

              $("#map_" + map.map_name + ' #legend-' + type_code).show();
              $("#map_" + map.map_name + ' #legend-' + type_code + ' > i').css('background-color', 'rgba(' + cv.join(",") + ')');
              $("#map_" + map.map_name + ' #legend-' + type_code + ' > i').css('border-color', color);
              $("#map_" + map.map_name + ' #legend-' + type_code + ' > i').css('border-width', weight);

              if(b_zoom && !b_tooltip) v_sous_titre.push(fp.label);
            });

          // chargement
          $("#" + map.map_name + " #chargement").hide();

          if(b_zoom) {
            v_sous_titre.length && add_sous_titre(v_sous_titre.join(', '), map);
            deferred_setBounds(featuresCollection.getBounds(), map, 5)
            .then(() => {
              setTimeout(()=>{
                var z = map.getZoom();
                var zoom_max_localisation = 15;
                var zoom_max_foret = 13;
                if(z > zoom_max_localisation && type=="localisation") {
                  map.setZoom(zoom_max_localisation);
                };
                if(z > zoom_max_foret && type=="foret") {
                  map.setZoom(zoom_max_foret);
                };

                resolve(2);

              }, 500)
            });
          }
          else {
            resolve(2);
          }
        }
      })
      });
      p.type=type;
      map.promises.push(p);
    };


    var d_degat_type_icon = {
      'Abr.': 'fa fa-seedling',
      'Éco.': 'fas fa-tree',
      'Sang.': 'fas fa-square',
      'Fro.': 'fas fa-angle-double-down',
      'P. & Clo.': 'fas fa-exclamation-triangle',
      'Abs.': 'fas fa-ban',
    };

    var d_degat_gravite_color = {
      "Fai.": 'yellow',
      "Mod.": 'orange',
      "Impt.": 'red',
    };

    var s_tooltip_degats = function(degats) {
      var s_tooltip = "";
      degats.forEach((degat) => {
        var color = 'white';
        var color_save = '';
        var cd_deg = degat.degat_type_mnemo;
        var icon = d_degat_type_icon[cd_deg];
        var _id_gravite = 0;

        degat.degat_essences.forEach((degat_essence) => {
          if (! degat_essence || ! degat_essence.degat_gravite_mnemo) return;
          color = d_degat_gravite_color[degat_essence.degat_gravite_mnemo];
          if (color == 'yellow' && ['red, orange'].includes(color_save)) {
            color = color_save;
          }
          if (color == 'orange' && color_save == 'red') {
            color = color_save;
          }
 
          color_save = color;
        });
        s_tooltip += '<i style="font-size:1em;color:' + color + '" class="' + icon +'"></i>';
      });
      return s_tooltip;
    }


    var s_popup_declaration = function(declaration) {
      var s_popup = "";
      s_popup += '<table class="table-sm table-popup">'
      s_popup += '<tr><th colspan="4"><a href="/declaration/declaration/' + declaration.id_declaration + '"  target="_blank">Alerte ' + declaration.id_declaration + ' </a></th></tr>'
      if(declaration.date) {
        s_popup += '<tr><th>Date</th><td colspan="3">' + declaration.date.split(" ")[0] + '</td></tr>'
      }
      s_popup += '<tr><th>Nom Foret</th><td colspan="3">' + declaration["label_foret"] + '</td></tr>'
      declaration.degats.forEach((degat) => {
        s_popup += '<tr><th colspan="4">' + degat.degat_type_label + '</th>';
        degat.degat_essences.forEach((degat_essence) => {
          s_popup += '<tr><td>' + degat_essence.degat_essence_label + '</td>';
          if(degat_essence.degat_gravite) {
            s_popup += '<td>' + (degat_essence.degat_gravite_mnemo) + '</td>';
            s_popup += '<td>' + (degat_essence.degat_etendue_mnemo) + '</td>';
            s_popup += '<td>' + (degat_essence.degat_anteriorite_mnemo) + '</td>';
          }
          s_popup +='</tr>'
        });
        s_popup += '</tr>';
      });
      s_popup += '</table>'
      return s_popup;
    }

    var s_legend_degats = function(declarations) {
      var s_legend = '<div style="background-color:lightgray; font-weight:bold">Types de dégâts</div>';
      var v_degat=[];
      declarations.forEach((declaration) => {

        declaration.degats.forEach((degat) => {
          var cd_deg = degat.degat_type_mnemo
          var label_deg = degat.degat_type_label
          if (! v_degat.includes(cd_deg)){
            v_degat.push(cd_deg);
            var icon = d_degat_type_icon[cd_deg];
            s_legend += '<div id="#legend-' + cd_deg + '"><i style="text-shadow: 0 0 0.3em #000000, 0 0 0.5em #000000; font-size:1.2rem; text-align:center;color:white; " class="' + icon + '"></i> ' + label_deg + '</div>';
          }
        });
      });
      s_legend += '<div style="background-color:lightgray; font-weight:bold">Gravité des dégâts</div>';
      s_legend += '<div><i style="text-shadow: 0 0 0.3em #000000, 0 0 0.5em #000000; font-size:1.2rem; text-align:center;color:yellow; " class="fas fa-square"></i> Faibles </div>';
      s_legend += '<div><i style="text-shadow: 0 0 0.3em #000000, 0 0 0.5em #000000; font-size:1.2rem; text-align:center;color:orange; " class="fas fa-square"></i> Moyens </div>';
      s_legend += '<div><i style="text-shadow: 0 0 0.3em #000000, 0 0 0.5em #000000; font-size:1.2rem; text-align:center;color:red; " class="fas fa-square"></i> Imortants </div>';

      return s_legend;
    }


    var load_declarations_centroid = function(declarations, map, config) {
    /* charge les centroids des déclarations
    */

    if(!config.centroid) return;

    var d_areas = {};
    var d_deg_color = {};

    if( ! map.markers && config.centroid.global) {
      map.markers = L.layerGroup();
      map.addLayer(map.markers);
      map.layerControl.addOverlay(map.markers, "Déclarations")
    }
    var k;
    for(k=0; k < declarations.length; k++) {

      var declaration = declarations[k];
      var id_declaration = declaration.id_declaration;
      var s_popup = s_popup_declaration(declaration);
      var centroid = declaration.centroid;
      var marker;
      if(config.centroid.type == "degat") {
        marker = L.circle(centroid);
        marker.bindTooltip(s_tooltip_degats(declaration.degats), {
          pane: 'PANE_5',
          permanent: true,
          direction: 'center',
          color: 'white',
          opacity: 1,
          fillOpacity: 1,
          interactive: true,
          className: ' tooltip tooltip-' + config.centroid.type,
        });

      } else if(config.centroid.type == "circle") {
        marker = L.circle(centroid);
        s_legend = '<div id="#legend-loc"><i style="color:black;font-size:0.5rem; text-align:center; transform:translateY(5px)" class="fas fa-circle"></i> ' + "Localisation des alertes" + '</div>';
      } else {
        marker = L.marker(centroid);
        s_legend = '<div id="#legend-loc"><i style="color:#257eca;font-size:1rem; text-align:center" class="fas fa-map-marker-alt"></i> ' + "Localisation de l'alerte" + '</div>';
      }
      L.setOptions(marker, { color: "black", radius: 100, pane: 'PANE_5'});
      marker.bindPopup(s_popup, {
        opacity: 1,
        pane: 'PANE_6',
      });
      marker.id_declaration = id_declaration;
      if(config.centroid.global) {
        map.markers.addLayer(marker);
      } else {
        map.addLayer(marker);
      }
      marker.on("click", function() {
        $(document).trigger("marker_click", [this.id_declaration]);
      });
    }

    // legend
    var s_legend;
    if(config.centroid.type == "degat") {
      s_legend += '<div id="#legend-loc"><i style="color:black;font-size:0.5rem; text-align:center; transform:translateY(5px)" class="fas fa-circle"></i> ' + "Localisation des alertes" + '</div>';
      s_legend = s_legend_degats(declarations)
    } else if(config.centroid.type == "circle") {
      s_legend = '<div id="#legend-loc"><i style="color:black;font-size:0.5rem; text-align:center; transform:translateY(5px)" class="fas fa-circle"></i> ' + "Localisation des alertes" + '</div>';
    } else {
      s_legend = '<div id="#legend-loc"><i style="color:#257eca;font-size:1rem; text-align:center" class="fas fa-map-marker-alt"></i> ' + "Localisation de l'alerte" + '</div>';
    }



    s_legend && $("#" + map.id + " .legend").append(s_legend);
  };

  // ajout des secteurs
  var add_secteurs = function(map, b_zoom=false) {
    var p = new Promise((resolve) => {
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
        resolve(2);
      });
      $("#" + map.id + " .legend").append('<div id="#legend-zc"><i style="background-color: rgb(184, 206, 145); border: 2px solid grey;"></i> ' +
        "Secteurs d'étude de l'Observatoire" + '</div>');
    });
    p.type = "secteurs";
    map.promises.push(p);
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
