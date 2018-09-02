$(document).ready(function() {

  "use strict";


  var get_db= function(type, key, val) {

    return  $.ajax({type: "GET", url: "/api/oeasc/get_db/" + type + "/" + key + "/" + val, async: false}).responseJSON;

  };


  var get_id_type = function(id_type) {

    return  $.ajax({type: "GET", url: "/api/ref_geo/get_id_type/" + id_type, async: false}).responseJSON;

  }

  M.get_db = get_db;
  M.get_id_type = get_id_type;

});
