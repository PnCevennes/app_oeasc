$(document).ready(function() {

  R = {};

  "use strict";

  var leaflet_hide_selector = ".leaflet-top.leaflet-right, .leaflet-top.leaflet-left";
  var leaflet_map_selector=".leaflet-map"

  var maptoPNG = function(id_element) {

    var map_node = document.getElementById(id_element);

    $(leaflet_hide_selector) && $(leaflet_hide_selector).hide();


    domtoimage.toPng(map_node).then(function (dataUrl) {
      var img = new Image();
      img.src = dataUrl;
      img.id = "img_" + id_element;
      $(map_node).after(img);
      $(map_node).hide();
      console.log("map2png")
    });


  };

  var toPDF = function(id_element) {

    var e = document.getElementById(id_element);
    html2pdf(e);

    console.log("html")

    return this;
  };

  var toPDF_map = function(id_element) {

    // transforme les cartes leaftlet en PNG
    console.log($("#"+id_element).find(leaflet_map_selector))

    var v1 = new Promise(function(resolve, reject) {
      $("#"+id_element).find(leaflet_map_selector).each(function(i, e){
        maptoPNG(e.id);
      });
      resolve();
    });

    var v2 = new Promise(function(resolve, reject) {

      var e = document.getElementById(id_element)
      html2pdf(e)
      .then(function() {
        return;
        $(leaflet_map_selector).show();
        $(leaflet_hide_selector).show();
        $(leaflet_map_selector).each(function(i, e){

          var after=$(e).after()
          if (after.is('img')) {
            after.remove();
          }
        });
      });
    });

    v1.then(v2);

  }

  R.toPDF_map = toPDF_map;
  R.toPDF = toPDF;

});
