$(document).ready(function() {

  "use strict";

  var get_choice = function(name) {

    var b = $("[name=" + name + "]:checked").val();

    if( (b == "T") || (b == "F") ) { 

      b = ( b == "T" ); 

    }

    return b;

  };


  var set_areas_cor = function(name, data_type, val, data_type_2, val_2) {

    var values = $('#' + name).val();

    if(values == "") {

      values=[];

    }

    else if( !(values instanceof Array) ) {

      values = [values];

    }

    var v = [];

    for(var i=0; i<values.length; i++) {

      var d = {};
      d.id_area = parseInt(values[i]);
      d[data_type_2] = val_2;

      v.push(d);

    }

    var s = JSON.stringify(v);

    $("#form_" + name).attr(data_type, s);

  };


  var get_from_flask_json = function(s) {

    s = s.replace(/{\'/g, '{"');
    s = s.replace(/\':/g, '":');
    s = s.replace(/: \'/g, ': "');
    s = s.replace(/, \'/g, ', "');
    s = s.replace(/\',/g, '",');
    s = s.replace(/\\xa0/g, '');
    s = s.replace(/\[\'/g, '["');
    s = s.replace(/\'\]/g, '"]');

    s = s.replace(/None/g, 'null');
    s = s.replace(/True/g, 'true');
    s = s.replace(/False/g, 'false');

    console.log(s);


    return JSON.parse(s);

  };


  var get_areas_cor = function(name, data_type) {

    return get_from_flask_json($("#form_" + name).attr(data_type));

    // var s = $("#form_" + name).attr(data_type).replace(/\'/g, '"').replace(/None/g, 'null');

    // var d = JSON.parse(s);

    // return d;

  };

  var get_cor = function(name, id_name,type="select") {

    var out = [];
    var s_add = "";

    if(type == "select") {

      s_add = " option:selected";

    } else {

      s_add = ":checked";

    }

    $("[name=" + name + "]" + s_add).each( function(i,e) {

      var d = {};
      d[id_name] = parseInt(e.value);
      out.push(d);

    });

    return out;

  };


  // recuperer proprietaire

  var get_id_proprietaire_as_dict = function() {

    var proprietaire = {};

    proprietaire.id_proprietaire = parseInt($('#form_proprietaire').attr('data-id-proprietaire'));

    proprietaire.id_declarant = parseInt($('#form_proprietaire').attr('data-id-declarant'));

    proprietaire.s_nom_proprietaire = $("#s_nom_proprietaire").val();
    proprietaire.s_telephone = $("#s_telephone").val();
    proprietaire.s_email = $("#s_email").val();
    proprietaire.s_adresse = $("#s_adresse").val();
    proprietaire.s_code_postal = $("#s_code_postal").val();
    proprietaire.s_commune_proprietaire = $("#s_commune_proprietaire").val();

    return proprietaire;

  };


  // récupérer les données du formulaire de proprietaire en dictionnaires

  var get_foret_as_dict = function() {

    var foret = {};

    foret.id_foret = parseInt($('#form_foret').attr('data-id-foret'));

    foret.b_statut_public = get_choice("b_statut_public");
    foret.b_document = get_choice("b_document");

    // foret.id_nomenclature_proprietaire_declarant = parseInt($("[name=id_nomenclature_proprietaire_declarant] option:selected").val());

    foret.s_nom_foret = $("#s_nom_foret").val();

    foret.proprietaire = get_id_proprietaire_as_dict();
    foret.id_proprietaire = foret.proprietaire.id_proprietaire;

    foret.areas_foret = get_areas_cor("areas_foret", "data-areas");

    foret.d_superficie = parseInt($("#d_superficie").val());

    return foret;
  };


  // récupérer les données du formulaire de declaration en dictionnaires

  var get_declaration_as_dict = function() {

    var declaration = {};

    // foret

    declaration.foret = get_foret_as_dict();
    declaration.id_foret = declaration.foret.id_foret;

    // id

    declaration.id_declaration = parseInt($('#form_declaration').attr('data-id-declaration'));

    // declarant

    declaration.id_declarant = parseInt($('#form_declaration').attr('data-id-declarant'));
    declaration.id_nomenclature_proprietaire_declarant = parseInt($("[name=id_nomenclature_proprietaire_declarant]:checked").val());



    // - degats

    declaration.degats = get_degats_as_dict();

    // - localisation

    // declaration.id_nomenclature_foret_type = parseInt($("[name=id_nomenclature_foret_type] option:selected").val());
    declaration.areas_localisation = get_areas_cor("areas_localisation", "data-areas");

    // - peuplement

    // - - essences

    declaration.id_nomenclature_peuplement_essence_principale = parseInt($("[name=id_nomenclature_peuplement_essence_principale] option:selected").val());
    declaration.nomenclatures_peuplement_essence_secondaire = get_cor("nomenclatures_peuplement_essence_secondaire", "id_nomenclature", "select");
    declaration.nomenclatures_peuplement_essence_complementaire = get_cor("nomenclatures_peuplement_essence_complementaire", "id_nomenclature", "select");

    // - - details

    declaration.id_nomenclature_peuplement_origine = parseInt($("[name=id_nomenclature_peuplement_origine]:checked").val());
    declaration.id_nomenclature_peuplement_type = parseInt($("[name=id_nomenclature_peuplement_type]:checked").val());
    declaration.nomenclatures_peuplement_maturite = get_cor("nomenclatures_peuplement_maturite", "id_nomenclature", "check");


    // - - protection

    declaration.b_peuplement_protection_existence = get_choice("b_peuplement_protection_existence");
    declaration.nomenclatures_peuplement_protection_type = get_cor("nomenclatures_peuplement_protection_type", "id_nomenclature", "check");;

    // - - paturage

    declaration.b_peuplement_paturage_presence = get_choice("b_peuplement_paturage_presence");
    declaration.nomenclatures_peuplement_paturage_type = get_cor("nomenclatures_peuplement_paturage_type", "id_nomenclature", "check");
    declaration.nomenclatures_peuplement_paturage_statut = get_cor("nomenclatures_peuplement_paturage_statut", "id_nomenclature", "check");
    declaration.id_nomenclature_peuplement_paturage_frequence = parseInt($("[name=id_nomenclature_peuplement_paturage_frequence]:checked").val());

    // - - autres

    declaration.id_nomenclature_peuplement_acces = parseInt($("[name=id_nomenclature_peuplement_acces]:checked").val());
    declaration.nomenclatures_peuplement_espece = get_cor("nomenclatures_peuplement_espece", "id_nomenclature", "check");;

    // - commentaires

    declaration.s_commentaire = $('#s_commentaire').val().trim();

    return declaration;

  };


  // récupérer les données du formulaire de dégats en dictionnaires

  var get_degats_as_dict = function() {

    var $form_degats = $("#form_degats");

    var degats = [];

    $form_degats.find("[name=nomenclatures_degat_type]:checked").each(function() {

      var degat = {};
      var id_degat = parseInt($(this).attr("degat-id-degat"));
      degat.id_degat = id_degat;

      var id_nomenclature_degat_type = parseInt(this.value);
      degat.id_nomenclature_degat_type= id_nomenclature_degat_type;

      var degat_essences = [];

      $(this).parent().find(".form-degat-essence").each(function() {

        var degat_essence = {};

        var id_degat_essence = parseInt($(this).attr("data-id-degat-essence"));

        degat_essence.id_degat_essence = id_degat_essence;

        var id_nomenclature_degat_essence = parseInt($(this).find("[name=id_nomenclature_degat_essence] option:selected").val());
        var id_nomenclature_degat_etendue = parseInt($(this).find("[name^=id_nomenclature_degat_etendue]:checked").val());
        var id_nomenclature_degat_gravite = parseInt($(this).find("[name^=id_nomenclature_degat_gravite]:checked").val());
        var id_nomenclature_degat_anteriorite = parseInt($(this).find("[name^=id_nomenclature_degat_anteriorite]:checked").val());

        degat_essence.id_nomenclature_degat_essence = id_nomenclature_degat_essence;
        degat_essence.id_nomenclature_degat_etendue = id_nomenclature_degat_etendue;
        degat_essence.id_nomenclature_degat_gravite = id_nomenclature_degat_gravite;
        degat_essence.id_nomenclature_degat_anteriorite = id_nomenclature_degat_anteriorite;

        degat_essences.push(degat_essence);

      });

      degat.degat_essences = degat_essences;
      degats.push(degat);

    });

    return degats;

  };


  M.get_areas_cor = get_areas_cor;
  M.set_areas_cor = set_areas_cor;
  M.get_declaration_as_dict=get_declaration_as_dict;
  M.get_foret_as_dict=get_foret_as_dict;
  M.get_degats_as_dict=get_degats_as_dict;
  M.get_cor = get_cor;
  M.get_from_flask_json = get_from_flask_json;
});
