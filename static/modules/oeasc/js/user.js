  $(document).ready(function() {

    "use strict";

    var test = 0;

    $('#organisme').hide();

    var get_json = function(id) {

      var d = $("#" + id).attr('data-' + id)
      if(d) {

        d = JSON.parse(d);

      }

      return d;

    }

    // get user
    var user = get_json('user');
    var id_app = parseInt($("#id_app").attr("data-id_app"));

    if(! user) {

      return;
    }

    function set_user(user_) {

      user = user_;
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

    console.log(test, user.id_role, id_app, user.organisme)

    if(test && !user.id_role) {

      user.nom_role = "CLEMENT";
      user.prenom_role = "Joel";
      user.email = "joelclems@gmail.com";
      user.id_organisme = $("#id_organisme option")[0].value;
      user.desc_role = "Salarié ou agent";
      user.organisme = "Mairie";

      $('#password').val("1234");
      $('#password_confirmation').val("1234");

    }


    var liste_organismes_oeasc = [];
    $('#id_organisme option').each((i, e) => liste_organismes_oeasc.push(e.innerHTML));


    $('#id_organisme').change(function() {

      var nom_organisme = $('#id_organisme :selected').html();

      console.log(nom_organisme)

      if (nom_organisme == "Autre (préciser)") {

        console.log(nom_organisme)
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

    set_user(user);

    if(user.id_role) {

      $('.input').hide();
      $('.password').hide();

    }

    else {

      $('.info').hide();

    }

    var show_error = function(elem="", msg="") {

      console.log(elem)
      console.log($("#" + elem))
      $("#login-error").html(msg).show();
      $("#" + elem).parent().before($("#login-error"));
      $([document.documentElement, document.body]).animate({
        scrollTop: $("#login-error").offset().top - 100
      }, 300);

    };
    var submit_form = function(e) {

      e.preventDefault();

      // gestion email
      var expressionReguliere = /^(([^<>()[]\.,;:s@]+(.[^<>()[]\.,;:s@]+)*)|(.+))@(([[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}])|(([a-zA-Z-0-9]+.)+[a-zA-Z]{2,}))$/;

      if(!expressionReguliere.test($('#email').val())) {

        show_error('email', "L'adresse email est invalide");
        return false;
      }

      // gestion mot de passe
      if( $('#user_pwd').val() != $('#user_pwd_conf').val()) {
        show_error('user_pwd', 'Les mots de passes ne correspondent pas.');
        return false;

      }

      // gestion identifiant (ici email) non unique et droits
      var user_;
      // si on a déjà un utilisateur avec ce mail
      if( (user_ = M.get_db('user', 'email',$('#user_email').val())) != "None") {

      // et qu'il a déjà les droits pour cette application
      if(user_.app_users.some(a => a.id_application == id_app)) {

        show_error('user_email', 'Cette adresse email est déjà utilisé pour cette application. Veuillez vous rendre à la <a href="' + "{{url_for('user.login')}}" + '?identifiant=' + user.email + '">page de connexion</a> ou choisir une adresse mail différente.');
        return false;

      } else {

        show_error('user_email', 'Un compte existe déjà avec cette adresse mail, mais il ne possède pas encore les droits pour cette application. Pour activer ce compte sur cette application <a href="' + "{{url_for('user.login')}}" + '?type=add_droit&identifiant=' + user.email + '">cliquer ici</a>.');
        return false;

      }

    }

    // gestion organisme non choisi
    if( $('#user_organism').val() == "" ) {

      show_error('user_organism', 'Choisir un organisme.');
      return false;

    }

    // gestion fonction non choisie
    if( $('#user_fonction').val() == "" ) {

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

    };

    $("#login-error").hide();

    var done;
    var url_post;
    if(!user.id_role) {

      url_post = '/pypn/register/post_usershub/create_temp_user'
      done = function(response) {
        console.log("done", response);
        $('#form_user').hide();
        $("#info_register").show();
      }

    } else {

      url_post = '/pypn/register/post_usershub/update_user'
      data.id_role = user.id_role;
      done = function(response) {
        console.log("done", response);
        $('.input').hide();
        $('.info').show();
        $("#modifier_infos").show();
        $("#info_update").show();
        set_user(response);

      }

    }

    console.log(url_post, user.id_role)

    $.ajax( {
      url : url_post,
      type: 'POST',
      data : JSON.stringify(data),
      contentType:"application/json; charset=utf-8",
      dataType:"json",
    }).done(done)
    .fail(function(error){
      console.log("fail", error)
      show_error("form_user", "Erreur : " + error.responseText)
      console.log(error);
    });


  };

  $("#form_user").submit(submit_form);

  $("#modifier_infos").click(function(e) {

    e.preventDefault();
    $('.info').hide();
    $('.input').show();
    $('#id_organisme').change();
    $("#modifier_infos").hide();

  });

});
