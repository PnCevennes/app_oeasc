$(document).ready(function() {

  "use strict";

  $(".button-supprimer-declaration").click(function() {

    var $this = $(this);
    var id_declaration = $this.attr('data-id-declaration');

    $.ajax({

      type: 'POST',
      url: "/api/oeasc/delete_declaration/" + id_declaration,

    }).done(function(response) {

      console.log("done : " + this.url);
      // $('#liste_declarations').html(response);
      $this.parents("tr").remove();

    }).fail(function(response) {

      console.log("fail : " + this.url, response);

    });

  });

});
