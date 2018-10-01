$(document).ready(function() {

  "use strict";


  M.declaration_effectuee = false;

  // pour retrouver le formulaire en cours

  var get_id_form = function() {

    return $('#id_form').attr('data-id-form');

  };


  // pour recharger le formulaire dans le cas des select a choix multiple (dès qu'ils perdent le focus)

  var f_select_focus_out = function() {

    var $this = $(this);

    setTimeout(function() {

      if (! $this.is(':visible') ) {

        recharger_form();

      }

    },100);

  };


  // on cree ici le chaînage des formulaires

  var initialiser_chainage_form = function() {

    var liste_forms = [];

    $('#form_container form').each(function() {

      liste_forms.push(this.id);

    });

    var d_config_form = {};

    liste_forms.forEach(function(e, i) {

      d_config_form[e] = {};

      var n = liste_forms.length;

      if( ( i - 1 ) >= 0 ) {

        d_config_form[e].prev=liste_forms[i - 1];

      }

      if( ( i + 1 ) <= n ) {

        d_config_form[e].next=liste_forms[i + 1];

      }

    });

    M.d_config_form =d_config_form;

  };


  // initialise formulaire foret

  var initialiser_form_foret = function() {

    $('[name=id_nomenclature_proprietaire_declarant]').change(function() {

      var declaration = M.get_declaration_as_dict();

      var s_proprietaire_declarant = $("[name=id_nomenclature_proprietaire_declarant]:checked").next().html().trim();

      if(s_proprietaire_declarant == "Oui, en son nom propre") {

        $('#form_proprietaire').attr('data-id-declarant', declaration.id_declarant)

      }

      recharger_form();

    });

    $('[name=b_statut_public], [name=b_document]').change(function() {

      // reset area_selection pour areas_localisation et areas_foret
      M.reset_foret();

      recharger_form();

    });

    $()
    $('#form_areas_foret select').change(function() {

      $("#form_areas_localisation").attr("data-areas", "[]");

    });

  };


  // initialise formulaire peuplement

  var initialiser_form_peuplement = function() {

    // essence

    $("#form_peuplement_essence select").selectpicker("refresh");

    $('#form_peuplement_essence select#id_nomenclature_peuplement_essence_principale').change(function() {

      recharger_form();

    });

    $('#form_peuplement_essence [id^="NOMENCLATURES_PEUPLEMENT_ESSENCE"] .bs-searchbox').focusout(f_select_focus_out);

    // details

    $('[name=id_nomenclature_peuplement_type]').change(function() {

      recharger_form();

    });

    // protection

    $('[name=b_peuplement_protection_existence]').change(function() {

      recharger_form();

    });

    // paturage

    $('[name=b_peuplement_paturage_presence]').change(function() {

      recharger_form();

    });

  };


  // initialise le formulaire des degats

  var initialiser_form_degats = function() {

    // bidouille pour avoir des formulaires imbriqués pour les dégats essences

    $(".form-degat-essence").each(function(i,e) {

      var $this =$(e);
      var html = $this.html();

      $this.html("");
      $this.append('<form></form>');
      $this.find("form").html(html);

    });

    $(".button-modifier-degat-essence").click(function() {

      var $this = $(this);
      var $degat_essence_affichage = $this.parents(".degat-essence").first();
      var $degat_button_essence_ajouter = $this.parents(".degat-essence-container").find("button.button-ajouter-degat-essence");
      var $degat_essence_form = $degat_essence_affichage.next();

      $degat_essence_affichage.hide();
      $degat_essence_form.show();
      $degat_button_essence_ajouter.prop("disabled", true);
      $("#form_degat_essence > input").prop("disabled", true);

    });

    $(".form-degat-essence form").submit(function(e) {

     e.preventDefault();
     recharger_form();

   });

    $(".button-undo-degat-essence").click(function(e) {

      var $this = $(this);
      var id_nomenclature_degat_type = $this.attr("data-degat-type");
      var id_nomenclature_degat_essence = $this.attr("data-degat-essence");

      if(id_nomenclature_degat_essence == "")
      {

        var $form_container =$this.parents(".form-degat-essence");
        $form_container.remove();
        return recharger_form();

      }

      return recharger_form(M.declaration_save);

    });

    $(".button-supprimer-degat-essence").click(f_supprimer_degat_essence);

    $(".button-ajouter-degat-essence").click(f_ajouter_degat_essence);

    // changement pour les type de degats

    $("[name=nomenclatures_degat_type]").change(function() {

      recharger_form();

    });

    $("#form_degats select").selectpicker("refresh");

  };



  var f_init_fil_ariane = function(selector) {

    var disabled = false;

    $(selector).each(function() {

      var $this = $(this);
      var id_form_cur = $this.attr("data-id-form");
      var id_form = get_id_form();

      var $form = $("#" + id_form_cur);

      disabled = (!$form[0].checkValidity()) || disabled;

      var declaration = M.get_declaration_as_dict();

      if(id_form_cur == "form_areas_localisation") {

        disabled = (declaration["areas_localisation"].length == 0);

      }

      if(id_form_cur == "form_areas_foret") {

        disabled = (declaration["foret"]["areas_foret"].length == 0);

      }

      if(disabled)
        $this.attr("disabled", disabled);

      var current =false;

      var fil = $this.parent().attr('id')

      if( fil == "fil_local") {

        current = ( id_form_cur == id_form );

      }

      if( fil == "fil_global") {

        $this.parent().next().children().each(function(index, elem) {

          current = current || ( $(elem).attr("data-id-form") == id_form_cur );

        });

      }

      $this.attr("current", current)

    });

  };


  var initialiser_form = function(id_form=null) {

    var declaration = M.get_declaration_as_dict()

    $(".fil-ariane a").unbind("click");

    $(".fil-ariane a").unbind("each");

    $(".fil-ariane a").click(function(e) {

      e.preventDefault();

      var $this =$(this)

      var id_form = $this.attr("data-id-form");

      if( !($this.attr("disabled") == "disabled") ) {

        recharger_form(null, id_form);

      }

    });

    if( ! id_form ) {

      id_form = get_id_form();

    }

    if( id_form == "form_areas_localisation" || id_form == "all" ) {

      setTimeout(function() { M.initialiser_form_localisation("form_areas_localisation"); }, 100);

    }

    if( id_form == "form_declaration" || id_form == "all" ) {

      M.remove_map(M["map_show_localisation"]);

      $('[href="#localisation"]').click(function (e) {

        if(! M["map_show_localisation"]) {

          setTimeout(function() { M.initialiser_show_localisation("show_localisation", declaration); }, 100);

        }

      });

    }

    if( id_form == "form_areas_foret" || id_form == "all" ) {

      setTimeout(function() { M.initialiser_form_localisation("form_areas_foret"); }, 100);

    }

    initialiser_form_foret();
    initialiser_form_peuplement();
    initialiser_form_degats();

    M.initialiser_checkbox_group_required();

    M.initialiser_tooltips();

    $('#form_container>form').submit(f_next);

    // on cache les formulaires

    if( id_form != "all") {

      $("#form_container").hide();

      // on commence avec le statut de la foret

      $("#form_display").html("");
      $("#form_display").append($("#fil_ariane"));
      $("#form_display").append($("#" + id_form));

    }

    else {

      $("#form_display").hide("");

    }

    f_init_fil_ariane("#fil_global a");
    f_init_fil_ariane("#fil_local a");

    window.onbeforeunload = function(){

      if (!M.declaration_effectuee) {

        // return confirm('Etes vous sur de vouloir quitter la page ?');

      }
    };

  };


  var f_next = function(e) {

    e.preventDefault();

    var id =this.id;

    var next = M.d_config_form[id].next;
    var prev = M.d_config_form[id].prev;

    var id_form = get_id_form();

    // si next existe on passe au suivant
    if(next) {

      if(["form_areas_foret", "form_areas_localisation"].includes(id)) {

        var type_code = $("#" + id + " .select_map").attr("data-type-code");

        if(["OEASC_COMMUNE", "OEASC_ONF_PRF"].includes(type_code)) {

          next = id;

        }

      }

      if(id_form == "all") {

        recharger_form(null, "all");

        $([document.documentElement, document.body]).animate({
          scrollTop: $("#" + next).offset().top - 100
        }, 300);

      }

      else {

        recharger_form(null, next);

      }

    }

    //s'il ny a plus de suivant on envoie le formulaire au backend
    else {

      var declaration = M.get_declaration_as_dict();

      $.ajax({

        type: 'POST',
        url: "/api/oeasc/create_or_update_declaration",
        data: JSON.stringify({
          "declaration": declaration,
          "id_form": get_id_form()
        }),
        contentType: "application/json",
        fail: function(response) {

          console.log("fail : " + this.url, response);

        },
      }).done(function(response) {

        M.declaration_effectuee=true


        console.log("done : " + this.url);
        console.log(response);

        $("#form_send").show();
        // $("#form_send").html(JSON.stringify(response));
        $("#form_display").hide();
        $("#form_container").hide();

        $("#btn_modal_merci").click();

      }).fail(function(response) {

        $("#form_display").html("<div>Votre formulaire n'a pas été envoyé.</div>" + response);

      });

    }

    return ;

  };


  //  on recharge le formulaire des dégats

  var recharger_form = function(declaration=null, id_form=null) {

    // on renseigne la declaration en cas de modification speciale (ie degats)
    // on renseigne le formulaire id_form si on change de formulaire, sinon il reste au formulaire courant

    if( declaration == null) {

      declaration = M.get_declaration_as_dict();

    }

    if( id_form == null) {

      id_form = get_id_form();

    }

    var foret = M.get_foret_as_dict();

    var data={"declaration": declaration, "id_form": id_form};

    console.log("beforeSend", data);

    $.ajax({

      type: 'POST',
      url: "/api/oeasc/get_form_declaration",
      data: JSON.stringify({

        "declaration": declaration,
        "id_form": id_form,
      }),
      contentType: "application/json",

    }).done(function(response) {

      console.log("done : " + this.url);

      $("#form_container").html(response);

      initialiser_form(id_form);

      M.declaration_save = M.get_declaration_as_dict();

    });

  };


  var f_ajouter_degat_essence = function() {

    var $this = $(this);
    var id_nomenclature_degat_type = $this.attr("data-degat-type");
    var declaration = M.get_declaration_as_dict();
    var degats = declaration.degats;

    // on rajouter un dictionnaire vide pour rajouter une ligne au essences pour le type de degat concerné

    for(var i=0; i< degats.length; i++) {

      var degat = degats[i];

      if (degat.id_nomenclature_degat_type == id_nomenclature_degat_type) {

        degat.degat_essences.push({});

      }

    }

    recharger_form(declaration);

  };


  var f_supprimer_degat_essence = function() {

    var $this = $(this);
    var id_nomenclature_degat_type = $this.attr("data-degat-type");
    var id_nomenclature_degat_essence = $this.attr("data-degat-essence");
    var declaration = M.get_declaration_as_dict();
    var degats = declaration.degats;

    for(var i=0; i< degats.length; i++) {

      var degat = degats[i];

      if (degat.id_nomenclature_degat_type == id_nomenclature_degat_type) {

        for(var j=0; j<degat.degat_essences.length; j++) {

          var degat_essence = degat.degat_essences[j];

          if (degat_essence.id_nomenclature_degat_essence == id_nomenclature_degat_essence) {

            degat.degat_essences.splice(j, 1);

          }

        }

      }

    }

    recharger_form(declaration);

  };


  // crsf

  $.ajaxSetup({

    beforeSend: function(xhr, settings) {

      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        var csrf_token = $("#csrf_token").attr("value");
        xhr.setRequestHeader("X-CSRFToken", csrf_token);

      }

    }

  });

  initialiser_chainage_form();
  initialiser_form();

  M.get_id_form = get_id_form;
});

