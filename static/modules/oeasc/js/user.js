  $(document).ready(function() {

    "use strict";

    $('#organisme').hide();

    var get_json = function(id) {

      var d = $("#" + id).attr('data-' + id)
      if(d) {

        d = JSON.parse(d);

      }

      return d;

    }

    var user = M.current_user;
    var user = JSON.parse($("#user").attr('data-user'));
    var id_application = M.config.ID_APP;

    console.log(user, id_application)

    if( ! user ) {

      return;
    }

    function set_user(user_in) {

      user = user_in;
      $('#nom_role').val(user.nom_role);
      $('#prenom_role').val(user.prenom_role);
      $('#email').val(user.email);
      $("#id_organisme").selectpicker('val', user.id_organisme);
      $("#organisme").val(user.organisme);
      $("#desc_role").selectpicker('val', user.desc_role);

      $('#info_nom_role').html(user.nom_role);
      $('#info_prenom_role').html(user.prenom_role);
      $('#info_email').html(user.email);
      $("#info_organisme").html(user.organisme);
      $("#info_desc_role").html(user.desc_role);

    }

    if(M.config.MODE_TEST && !user.id_role) {

      user.nom_role = "CLEMENT";
      user.prenom_role = "Joel";
      user.email = "joel.clement@cevennes-parcnational.fr";
      user.organisme = "Mairie";
      user.id_organisme = $("#id_organisme option")[1].value;
      user.desc_role = "Salarié ou agent";

      $('#password').val("1234");
      $('#password_confirmation').val("1234");

    }


    var liste_organismes_oeasc = [];
    $('#id_organisme option').each((i, e) => liste_organismes_oeasc.push(e.innerHTML));


    $('#id_organisme').change(function() {

      var nom_organisme = $('#id_organisme :selected').html();

      if (nom_organisme == "Autre (préciser)") {

        $('#organisme').show();
        $('#organisme').prop('required', true);

        if(liste_organismes_oeasc.includes($("#organisme").val())) {

          $('#organisme').val('');

        }

      } else {

        $('#organisme').hide();
        $('#organisme').prop('required', false);
        $('#organisme').val(nom_organisme);

      }

    });

    if(user.nom_role) set_user(user);

    if(user.id_role) {

      $('.input').hide();
      $('.password').hide();

      $('.info').show();

    }

    else {

      $('.info').hide();
      $('.input').show();


    }

    var show_error = function(elem="", msg="") {

      $("#login-error").html(msg).show();
      $("#" + elem).parent().after($("#login-error"));
      $([document.documentElement, document.body]).animate({
        scrollTop: $("#login-error").offset().top - 100
      }, 300);

    };
    var submit_form = function(e) {

      e.preventDefault();

    $('#email').parent().prev().prev().css('color', 'black')
    $('#id_organisme').parents("td").prev().prev().css('color', 'black')
      // gestion email
      var expressionReguliere = /^(([^<>()[]\.,;:s@]+(.[^<>()[]\.,;:s@]+)*)|(.+))@(([[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}])|(([a-zA-Z-0-9]+.)+[a-zA-Z]{2,}))$/;

      if(!expressionReguliere.test($('#email').val())) {

        show_error('email', "L'adresse email est invalide");
        return false;
      }


      if(! user.id_role) {

        // gestion identifiant (ici email) non unique et droits
        // var user_from_mail = M.get_db('user', 'email',$('#email').val());
        var user_from_mail = $.ajax({type: "GET", url: "/api/user/get_user_from_email/" + $('#email').val(), async: false}).responseJSON;;

        console.log(user_from_mail);

        // si on a déjà un utilisateur avec ce mail
        if( !(user_from_mail == "None" || !user_from_mail)) {

        // et qu'il a déjà les droits pour cette application
        if(user_from_mail.id_droit_max) {

          show_error('email', '<p>Cette adresse email est déjà utilisé pour cette application.</p> \
            <p>Veuillez vous identifier à la \
            <a href="/user/login?identifiant=' + user_from_mail.email + '">\
            page de connexion\
            </a> ou choisir une adresse mail différente.</p>');
          return false;

        } else {

          show_error('email', '<p>Un compte existe déjà avec cette adresse mail,\
            mais il ne possède pas encore les droits pour cette application.</p> \
            <p>Pour activer ce compte sur cette application \
            <a href="/user/login?type=add_droit&identifiant=' + user.email + '">\
            cliquer ici\
            </a>.</p>');
          return false;

        }

      }

    }

      // gestion mot de passe
      if( $('#password').val() != $('#password_confirmation').val()) {
        show_error('password', 'Les mots de passe renseignés ne correspondent pas.');
        return false;

      }

    // gestion organisme non choisi
    if( $('#organism').val() == "" ) {

      show_error('user_organism', 'Choisir un organisme.');
      return false;

    }

    // gestion fonction non choisie
    if( $('#fonction').val() == "" ) {

      show_error("#user_fonction", "Choisir une fonction.")
      return false;

    }

    var data = {

      "nom_role": $('#nom_role').val(),
      "prenom_role": $('#prenom_role').val(),
      "identifiant": $('#email').val(),
      "email": $('#email').val(),

      "password": $('#password').val(),
      "password_confirmation": $('#password_confirmation').val(),

      "groupe": false,
      "pn": true,
      "remarques": "creé depuis le site OEASC",
      "id_unite": -1,
      "id_organisme": $('#id_organisme').val(),
      "organisme": $('#organisme').val().substr(0,32),
      "desc_role": $('#desc_role').val(),

      "id_application": id_application

    };


    $("#login-error").hide();

    var done;
    var url_post;
    if(!user.id_role) {

      url_post = '/pypn/register/post_usershub/create_temp_user'
      done = function(response) {
        $("#pending").hide();
        $('#form_user').hide();
        $("#info_register").show();
      }

    } else {

      url_post = '/pypn/register/post_usershub/update_user'
      data.id_role = user.id_role;
      done = function(response) {
        $("#pending").hide();
        $('#form_user').show();
        $('.input').hide();
        $('.info').show();
        $("#modifier_infos").show();
        $("#info_update").show();
        set_user(response);

      }

    }

    $("#form_user").hide();
    $("#pending").show();
    $.ajax( {
      url : url_post,
      type: 'POST',
      data : JSON.stringify(data),
      contentType:"application/json; charset=utf-8",
      dataType:"json",
    }).done(done)
    .fail(function(data){
      var msg = data.responseJSON ? data.responseJSON.msg : data.responseText
      console.log("fail", data, msg)
      show_error("form_user_top", "Erreur : " + msg)
    });


  };

  $("#form_user").submit(submit_form);

  $("#modifier_infos").click(function(e) {

    e.preventDefault();
    $('.info').hide();
    $('.input').show();
    $('#id_organisme').change();
    $('#id_organisme').change();
    $('#email').prop("disabled", true);
    $('#id_organisme').prop("disabled", true);
    $('#id_organisme').selectpicker('refresh');

    $('#email').parent().prev().prev().css('color', 'lightblue')
    $('#id_organisme').parents("td").prev().prev().css('color', 'lightblue')

    $('#organisme').prop("disabled", true);

    $("#modifier_infos").hide();

  });

});
