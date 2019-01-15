$(document).ready(function() {

  R = {};

  "use strict";

  var leaflet_hide_selector = ".leaflet-top.leaflet-right, .leaflet-top.leaflet-left";
  var leaflet_map_selector=".leaflet-map"



  var maptoPNG = function(id_element) {
    return new Promise((resolve, reject) => {

      if(!id_element) { resolve(); return};

      var map_node = document.getElementById(id_element);

      $(leaflet_hide_selector) && $(leaflet_hide_selector).hide();

      domtoimage.toPng(map_node).then(function (dataUrl) {
        var img = new Image();
        img.src = dataUrl;
        img.id = "img_" + id_element;
        $(map_node).after(img);
        $(map_node).hide();
        resolve();
      });

    });
  };

  var toPDF = function(id_element) {
    return new Promise((resolve, reject) => {
      var e = document.getElementById(id_element);
      $(e).addClass("pdf");

      var opt = [];
      html2pdf(e, opt).then(() => {
        $(e).removeClass("pdf");
        resolve();
      });

    });
  };

  var toPDF_map = function(id_element) {

    // transforme les cartes leaftlet en PNG

    var f_array = [];

    $("#"+id_element).find(leaflet_map_selector).each(function(i, e){
      f_array.push(maptoPNG(e.id));
    });

    Promise.all(f_array).then(() => {
      toPDF(id_element)
      .then(() => {
        $(leaflet_map_selector).show();
        $(leaflet_hide_selector).show();
        $(leaflet_map_selector).each(function(i, e){

          var next=$(e).next()
          if (next.is('img')) {
            next.remove();
          }
        });
      });
    });

  }

  R.toPDF_map = toPDF_map;
  R.toPDF = toPDF;

});
