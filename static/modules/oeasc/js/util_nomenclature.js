$(document).ready(function() {

  N={};

  "use strict";

  var get_nomenclature_mnemonique = function(id_nomenclature) {
    if(id_nomenclature != ""){

      var responseText = $.ajax({type: "GET", url: "/api/oeasc/get_nomenclature_mnemonique/" + id_nomenclature, async: false}).responseText;
      return responseText.replace(/\"/g, "");
    }
    return "";
  };

  N.get_nomenclature_mnemonique = get_nomenclature_mnemonique;
});
