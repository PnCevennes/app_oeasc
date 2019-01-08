$(document).ready(function() {

  "use strict";



var reset_proprietaire = function() {

    $('#form_proprietaire').attr('data-id-proprietaire', "");

    $("#nom_proprietaire").val("");
    $("#telephone").val("");
    $("#email").val("");
    $("#adresse").val("");
    $("#s_code_postal").val("");
    $("#s_commune_proprietaire").val("");
    // $("#id_nomenclature_proprietaire_type").val("");


}

  var reset_foret = function() {

    reset_proprietaire();

    // re-initialise data-areas foret, data-areas localisation et id_foret
    $("#form_areas_localisation").attr("data-areas", "[]");
    $("#form_areas_foret").attr("data-areas", "[]");
    $('#form_foret').attr('data-id-foret', "");
    $("#nom_foret").val("");
    $("#label_foret").val("");
    $("#surface_renseignee").val("");

  };

  var get_choice = function(name) {

    var b = $("[name=" + name + "]:checked").val();

    if( (b == "T") || (b == "F") ) { 

      b = ( b == "T" ); 

    }

    return b;

  };


  var set_areas_cor = function(form_id, type_code, val, data_type_2, val_2) {

    // form_id "form_area_foret" ou "form_area_localisation"
    // type_code OEASC_CADASTRE, ect...
    // data_type_2 id_declaration ou id_foret

    var v_init = get_areas_cor(form_id);
    v_init = v_init.filter(area => area.type_code != type_code);

    var values = $('#' + type_code).val();

    if(values == "") {

      values = [];

    }

    else if( !(values instanceof Array) ) {

      values = [values];

    }

    var v = [];

    for(var i=0; i<values.length; i++) {

      var d = {};

      d.id_area = parseInt(values[i]);
      d[data_type_2] = val_2;
      d["type_code"] = type_code;

      v.push(d);

    }

    v = v_init.concat(v);

    var s = JSON.stringify(v);

    $("#" + form_id).attr("data-areas", s);

  };


  var get_areas_cor = function(form_id, type_code="") {

    // form_id "form_area_foret" ou "form_area_localisation"
    // type_code OEASC_CADASTRE, ect...

    var s = $("#" + form_id).attr("data-areas");

    if(!s) {

      return [];

    }

    var out = JSON.parse(s);

    if(type_code) {

      out = out.filter(area => area.type_code == type_code);

    }

    return out;

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
    proprietaire.id_nomenclature_proprietaire_type = parseInt($('#form_proprietaire').attr('data-id-nomenclature-proprietaire-type'));

    proprietaire.nom_proprietaire = $("#nom_proprietaire").val();
    proprietaire.telephone = $("#telephone").val();
    proprietaire.email = $("#email").val();
    proprietaire.adresse = $("#adresse").val();
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

    foret.label_foret = $("#label_foret").val();
    foret.nom_foret = foret.label_foret;
    foret.code_foret = foret.label_foret;


    foret.proprietaire = get_id_proprietaire_as_dict();
    foret.id_proprietaire = foret.proprietaire.id_proprietaire;

    foret.areas_foret = get_areas_cor("form_areas_foret");

    // foret.superficie = parseInt($("#superficie").val());
    foret.surface_renseignee = parseInt($("#surface_renseignee").val());
    foret.surface_calculee = foret.surface_renseignee;

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
    declaration.areas_localisation = get_areas_cor("form_areas_localisation");


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

    if($('#autre_protection').length) {

      declaration.autre_protection = $('#autre_protection').val().trim();

    } else {

      declaration.autre_protection = '';

    }

    // - - paturage

    declaration.b_peuplement_paturage_presence = get_choice("b_peuplement_paturage_presence");
    declaration.id_nomenclature_peuplement_paturage_type = parseInt($("[name=id_nomenclature_peuplement_paturage_type]:checked").val());
    declaration.nomenclatures_peuplement_paturage_statut = get_cor("nomenclatures_peuplement_paturage_statut", "id_nomenclature", "check");
    declaration.id_nomenclature_peuplement_paturage_frequence = parseInt($("[name=id_nomenclature_peuplement_paturage_frequence]:checked").val());
    declaration.nomenclatures_peuplement_paturage_saison = get_cor("nomenclatures_peuplement_paturage_saison", "id_nomenclature", "check");

    // - - autres

    declaration.id_nomenclature_peuplement_acces = parseInt($("[name=id_nomenclature_peuplement_acces]:checked").val());
    declaration.nomenclatures_peuplement_espece = get_cor("nomenclatures_peuplement_espece", "id_nomenclature", "check");;


    // - commentaires

    declaration.commentaire = $('#commentaire').val().trim();

    return declaration;

  };


  // récupérer les données du formulaire de dégâts en dictionnaires

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
  M.reset_foret = reset_foret;
  M.reset_proprietaire = reset_proprietaire;

});
