$(document).ready(function() {

  'use strict';

  // pour gerer les requires avec les checkbox group
  // attention à bien renseigner les name

  var f_checkbox_group = function() {

    var $this = $(this);
    var name = $this.attr('name');

    var $group=$('.checkbox-group-required input[name=' + name + ']');

    $group.prop("required", true);

    // modification du message d'erreur

    $group.each(function (i,elem) {

      elem.setCustomValidity("");

      elem.oninvalid = function(e) {

        e.target.setCustomValidity("");

        if (!e.target.validity.valid) {

          e.target.setCustomValidity("Sélectionner un élément dans la liste");

        }

      };

      elem.oninput = function(e) {

        e.target.setCustomValidity("");

      };

    });

    if(name) {

      // si un seul est checked on enleve les required

      if( $('.checkbox-group-required input[name=' + name + ']:checked').length > 0 ) {

        $group.prop("required", false);

      }

      // sinon on remet les required

      else {

        $group.prop("required", true);

      }

    }

  };


  var initialiser_checkbox_group_required = function() {

    $(".checkbox-group-required > div > input").prop("required", true);
    $(".checkbox-group-required > div > input").each(f_checkbox_group);
    $(".checkbox-group-required > div > input").change(f_checkbox_group);

  };


  var initialiser_tooltips = function() {

    $(".custom-tooltip").each(function(index, elem) {

      var $elem = $(elem);

      $("label[for=" + $elem.attr("data-name") + "]").find(".custom-tooltip").remove();
      $("label[for=" + $elem.attr("data-name") + "]").append(" ");
      $("label[for=" + $elem.attr("data-name") + "]").append($elem.clone());

    });

  };


  M.initialiser_checkbox_group_required = initialiser_checkbox_group_required;
  M.initialiser_tooltips = initialiser_tooltips;


});
