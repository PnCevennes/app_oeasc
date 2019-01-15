$(document).ready(function() {

  "use strict";

  // fonctions pour gérer les carte ( + select) de selection de foret, communes, section, UG ou parcelles

  var initialiser_form_localisation = function(id_form) {
  /* initialisation du formulaire

    id_form : pour repérer la partie du formulaire concernée
    */
    $('#' + id_form + ' .select_map').each(function() {

      M[id_form] = {}
      M[id_form].b_loaded = false;

      // type de donnée pour la requête : OEASC_ONF_FRT, OEASC_CADASTRE, ...
      var type_code = $(this).attr("data-type-code");

      if(type_code) {
        initialiser_select_map(type_code);
      }

    });

  }

  var initialiser_select_map = function(map_name) {
  /* initialisation du select_map

    map name:
    */

    // initialisation carte
    var map = M.init_map(map_name);
    var id_select_map = 'select_map_' + map_name;

    // initialisation des legendes pour tout les type présents dans M.list.data
    M.list.data.forEach(function(name) {
      var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + M.d_ls[name].label + '</div>';
      $('#' + id_select_map).find(".legend").append(s_legend);
    });

    // on cache ttes les légendes
    M.list.data.forEach(function(e) {
      $('#' + id_select_map).find("#legend-" + e).hide();
    });

    // légende selection orange
    name="LOCALISATION_SELECTION";
    var s_legend = '<div id="legend-' + name + '"><i style="background: ' + M.color[name] + '; border: 1px solid black;"></i> ' + "Sélection" + '</div>';
    $('#' + id_select_map).find(".legend").append(s_legend);

    // ajout du change sur click selectpicker ..?
    $('#' + name).parent().find('.bs-select-all').click( function() {
      $('#' + name).change();
    });

    // les tooltip des layer s'affichent (et s'effacent) au survol des options
    $('#' + id_select_map + " .localisation-select").on("mouseover", "ul.inner > li", f_option_hover(map));
    $('#' + id_select_map + " .localisation-select").on("mouseout", "ul.inner > li", f_option_hover(map));

    // données depuis html
    // type_code depuis html ?? (depuis map_name TODO)
    var type_code = $("#select_map_" + map_name).attr("data-type-code");
    var areas_container = JSON.parse($("#select_map_" + map_name).attr("data-areas-container"));

    load_select_map_data(map, type_code, areas_container)

    if(areas_container.length > 0) {
      var type = "foret";
      if (areas_container[0].type_code=="OEASC_ONF_PRF") {
        type = 'localisation';
      }
      M.load_areas(areas_container, type, map, false);
    }

  };


  var f_change = function(map) {
    return function(e) {
  /* fonction pour gérer les changement de selection de select_map
    et pour gérer les interactions carte-select côté select
  */
      var $this = $(this);
      var values = $(this).val();
      if(values == "") {
        values=[];
      } else if( !(values instanceof Array) ) {
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
          layer_on_click(_layer, map);
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
          layer_on_click(l, map);
        }
      }

    };
  };

  var layer_on_click = function(layer, map) {
  /* fonction pour gérer les changement de selection de select_map
    et pour gérer les interactions carte-select côté carte

    layer: element de carte cliqué à sélectionner ou dé-sélectionner
    map: objet carte leaflet
  */

    if(!layer) return false;

    var $select = $("#" + map.map_name);
    var fp = layer.feature.properties;
    var name = fp.name;
    var ls = M.d_ls[name];

    if(layer.selected) {
      // si déjà sélectionné on dé-selectionne
      layer.setStyle({
        color: M.color.p2,
        fillColor: M.color.p2
      });
      layer.selected = false;
      $select.find("option[value=" + fp.id_area + "]").prop("selected", false);

    } else {
      // sinon on sélectionne
      layer.setStyle({
        color: M.color.selected,
        fillColor: M.color.selected
      });
      if( ! $select.prop("multiple") ) {
        // gestion selection multiple
        $select.find("option:selected").prop("selected", false);
        get_layer_selected(map).forEach(function(_layer){
          _layer.setStyle({
            color: M.color.p2,
            fillColor: M.color.p2
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
      // ajout dans input areas_foret
      form_name = "form_areas_foret"
      data_type_2 ="id_foret";
      val = parseInt($("#form_foret").attr("data-id-foret"));
    }


    if( M.type_codes_areas_localisation.indexOf(map.map_name )>= 0 ) {
      // ajout dans input areas_localisation
      form_name = "form_areas_localisation";
      data_type_2 ="id_declaration";
      val = parseInt($("#form_declaration").attr("data-id-declaration"));
    }

    M.set_areas_cor(form_name, name, $select.val(), data_type_2, val);

    if(form_name == "form_areas_foret" && M["form_areas_foret"].b_loaded) {
      $("#form_areas_localisation").attr("data-areas", "[]");
    }

    // $select.selectpicker('render');
    $select.selectpicker("refresh")
    f_sort_selected(name);
  };


  var f_sort_selected = function(name) {
    /* tri pour les selections multiple
      par ordre alphabetique
      et éléments sélectionnés en haut de liste
    */

    if ( ["OEASC_ONF_FRT", "OEASC_DGD"].includes(name) ) {
      return ;
    }

    var $select = $('#' + name);
    var opts_list = $select.find('option');

    opts_list = opts_list.sort(function(a, b) {
      if (a.selected == b.selected) {
        if ( ["OEASC_ONF_PRF", "OEASC_ONF_UG"].includes(name) ) {
          return parseInt(a.innerHTML) > parseInt(b.innerHTML)? 1 : -1;
        } else {
          return a.innerHTML > b.innerHTML? 1 : -1;
        }
      } else {
        return a.selected ? -1 : 1;
      }
    });

    $select.html('').append(opts_list);
    $select.selectpicker("refresh")
  }


  var process_select_map_data = function(map, name) {
    return function(response) {
    /* fonction pour exploiter les données reçues

    response: reponse de la requete ajax
    map: objet carte leaflet
    name: nom de la donnée voulue ex "OEASC_CADASTRE"
    - response: reponse de la requete ajax
    */

      // add layers to map
      var id_select_map = "select_map_" + map.map_name;
      var features_collection = L.geoJson(response, {
          pane: 'PANE_3'
        });
      features_collection.addTo(map);
      var nb_layers = Object.keys(features_collection._layers).length;

      if(nb_layers == 0) {
        $('#' + id_select_map + " #chargement").hide();
        // gérer le cas ONF PRF sans UG
        var id_form = $('#id_form').attr('data-id-form');
        if ( name == 'OEASC_ONF_UG' && id_form == "form_areas_localisation") {
          $("#" + name).parent().hide();
          $('#form_areas_localisation select').prop('required', false)
          $('#form_areas_localisation #info_no_UG').show()
          return;
        }
      }

      M.deferred_setBounds(features_collection.getBounds(), map);

      // HTML select
      var $select = $("#" + name);

      // pour chaque layers
      features_collection.eachLayer(function(layer) {

        //style
        layer.setStyle(M.style.default);
        layer.setStyle({
          color: M.color.p2,
          fillColor: M.color.p2
        });

        var fp = layer.feature.properties;
        fp.name = name;

        // tooltips
        layer.bindTooltip(fp.label, {opacity: 1, pane: 'PANE_5'}).addTo(map);

        //select option
        $select.append('<option value="' + fp.id_area + '"> ' + fp.label + ' </option>');

        //mouse events
        layer.on("mouseover", function (e) {
          layer.setStyle(M.style.highlight);
        });

        layer.on("mouseout", function (e) {
          layer.setStyle(M.style.default);
        });

        layer.on("click", function (e) {
          if(map.map_name == 'OEASC_DGD' || map.map_name == 'OEASC_ONF_FRT') {
            M.reset_foret();
          }
          // gestion sélection/désélection sur carte
          layer_on_click(layer, map);
        });

      });

      // init carte et select avec selection en cours
      var form_id = $select.parents("form").attr("id");
      var areas = M.get_areas_cor(form_id, name);

      if($select.val()) {
        $select.val("");
      }

      for(var i=0; i < areas.length; i++) {
        var l = M.get_layer(map, 'id_area', areas[i].id_area);
        if(l) {
        layer_on_click(l, map);
        }
      }

      var selected = $select.val();
      // init selectpicker
      $select.selectpicker();
      $select.change(f_change(map));

      // patch : refaire la sélection après init selectpicker
      if( selected &&  $select.val()=="" ) {
        $select.val(selected);
        $select.selectpicker("refresh");
      }

      // tri pour les selections multiple
      // par ordre alphabetique
      // et éléments sélectionnés en haut de liste
      f_sort_selected(name);

      M[form_id].b_loaded=true;

      $('#' + id_select_map + " #chargement").hide();
      console.log("Map : " + String(nb_layers) + " elements chargés pour " + name + " selected : " + $select.val());

      // cas UG unique
      // rien pour l'instant

      // var id_form = $('#id_form').attr('data-id-form');
      // if ( name == 'OEASC_ONF_UG' && id_form == "form_areas_localisation") {
      //   var areas_container = JSON.parse($("#" + id_select_map).attr("data-areas-container"));
      //   // cas nb_UG == nb_PRF
      //   if(areas_container.length == nb_layers) {
      //     // sélection de toutes les UG
      //     $(".bs-select-all").click()
      //     // on passe au suivant
      //     $('#form_areas_localisation input').click()
      //   }
      // }
    }
  }


  var process_select_map_data_fail = function(map, name) {
    return function(response) {
    /* fonction pour gérer le pb dechargement de données

    map: objet carte leaflet
    name: nom de la donnée voulue ex "OEASC_CADASTRE"
    - response: reponse de la requete ajax
    */
      $('#' + id_select_map + " #chargement").hide();

      // TODO
      // gérer le cas ONF PRF sans UG
      if ( name == 'OEASC_ONF_UG' && id_form == "form_areas_localisation") {
        // on passe au suivant
        $('#form_areas_localisation select').attr('required', false)
        $('#form_areas_localisation input').click()
      }
      console.log("fail", response);
    }
  }

  var load_select_map_data = function(map, name, areas_container=[]) {
    /* fonction pour charger les données et initialiser le select_map

      map: objet carte leaflet
      name: nom de la carte et de l'object a charger (ex OEASC_CADASTRE)
      areas_container: tableau des aires (dict) des contenants
    */

    var id_select_map = "select_map_" + map.map_name;

    $("#legend-" + name).show(); // legend de "name"
    $('#' + name).show(); // select

    var url;

    // contruction url data
    if( areas_container.length > 0 ) {
      url = "/api/ref_geo/areas_simples_from_type_code_container/l/";
      url+= name + "/"
      url+= areas_container.map(e => e.id_area).join("-");
    } else {
      url = "/api/ref_geo/areas_simples_from_type_code/l/" + name;
    }

    // requete ajax
    $.ajax({
      type: "POST",
      url: url,
      contentType:"application/json; charset=utf-8",
      dataType:"json"
    }).done(process_select_map_data(map, name))
    .fail(process_select_map_data_fail(map, name));

    $("#" + id_select_map + " #chargement").show(); // affichage chargement en cours
  }



  var get_layer_selected = function(map){
  /* recupere tous les layers selectionnne (en orange sur la carte)
  */

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

  var f_option_hover = function(map) {
    return function(e) {
    /* pour afficher les tooltip quand un élément est survolé dans la liste de sélection

     map : map leaflet
     - e : event ici mouseout ou mouseover
     */

      // close all tooltips, pour éviter les tooltips qui traînent
      map.eachLayer(function(layer) {
        if(layer._tooltip) { layer.closeTooltip(); }
      });

      var $this = $(this);
      var label = $this.find('.text').html().trim();
      // get layer
      var l = M.get_layer(map, "label", label);

      // fire mouseout or mouseover event
      // le layer réagit en fermant ou en ouvrant le tooltip
      if( l ) { l.fire(e.type); }
    };
  };


  // sauvegarde dans la variable globale M
  M.initialiser_form_localisation = initialiser_form_localisation;

});
