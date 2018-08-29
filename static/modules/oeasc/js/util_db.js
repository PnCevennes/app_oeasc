$(document).ready(function() {

  "use strict";


  var get_db= function(type, key, val) {

    return  $.ajax({type: "GET", url: "/api/oeasc/get_db/" + type + "/" + key + "/" + val, async: false}).responseJSON;

  };

  M.get_db = get_db;

});
