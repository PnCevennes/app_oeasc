$(document).ready(function() {

  "use strict";


  var get_db= function(type, key, val) {

    return  $.ajax({type: "GET", url: "/api/oeasc/get_db/" + type + "/" + key + "/" + val, async: false}).responseJSON;

  };


  var get_id_type = function(id_type) {

    return  $.ajax({type: "GET", url: "/api/ref_geo/get_id_type/" + id_type, async: false}).responseJSON;

  }

  var get_type_code = function(id_type) {

    if( ! M.type_codes) {

      M.type_codes = $.ajax({type: "GET", url: "/api/ref_geo/type_codes_oeasc", async: false}).responseJSON;

    }

    var e = M.type_codes.filter(e => e.id_type == id_type);

    if (!e) { return "";}

    return e[0].type_code



  }

  M.get_db = get_db;
  // M.get_id_type = get_id_type;
  M.get_type_code = get_type_code;

});
