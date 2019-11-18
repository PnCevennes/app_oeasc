$(document).ready(function() {

  var leaflet_hide_selector = ".leaflet-top.leaflet-right, .leaflet-top.leaflet-left";
  var leaflet_map_selector=".leaflet-map"

  var cpt_maps = 0;
  var nb_maps= 0;

  var maptoPNG = function(id_element) {
    /*
    transforme les elements leaflet map en PNG
    ici cache les element definis par leaflet_hide_selector (zoom, controls, etc..)
    puis chache la carte pour pouvoir ensuite en faire un pdf
    */
    return new Promise((resolve, reject) => {

      if(!id_element) { resolve(); return};

      var map_node = document.getElementById(id_element);
      $(leaflet_hide_selector) && $(leaflet_hide_selector).hide();

      M.wait_for_map_loaded(M[id_element]).then(()=>{
        setTimeout(()=>{
          domtoimage.toPng(map_node,
          {
            height: Math.floor($(map_node).height()),
            witdh: Math.floor($(map_node).width())
          }).then(function (dataUrl) {
            cpt_maps += 1;
            $("#pdf_infos") && $("#pdf_details").html("Création des cartes : " + cpt_maps + " sur " + nb_maps);

            var img = new Image();
            img.src = dataUrl;
            img.id = "img_" + id_element;
            $(map_node).after(img);
            $(img).addClass("img-pdf");
            $(map_node).hide();
            resolve();
          });
        }, 1000);
      });
    });
  };

  var toPDF = function(id_element) {
    return new Promise((resolve, reject) => {
      var e = document.getElementById(id_element);
      $(e).addClass("pdf");

      var opt = {
        pagebreak: {
          mode: 'avoid-all',
        },
        html2canvas: {dpi: 72, letterRendering: true},
      };
      var filename = $('#' + id_element).attr('filename');
      if(filename) {
        opt['filename'] = filename;
      }
      html2pdf(e, opt).then(() => {
        $(e).removeClass("pdf");
        resolve();
      });
    });
  };

  var toPDF_map = function(id_element) {
    // transforme les cartes leaftlet en PNG
    return new Promise((resolve, reject) => {

      console.log("#pdf_infos", $("#pdf_infos"), id_element)
      $("#pdf_infos") && $("#pdf_infos").show()

      var f_array = [1];

      var e = document.getElementById(id_element);
      $(e).addClass("pdf");

      nb_maps = $("#"+id_element).find(leaflet_map_selector).length;
      cpt_maps = 0;
      $("#pdf_infos") && $("#pdf_details").html("Création des cartes : " + cpt_maps + " sur " + nb_maps);

      $("#"+id_element).find(leaflet_map_selector).each(function(i, e){
        M[e.id].invalidateSize();
      });

      $("#"+id_element).find(leaflet_map_selector).each(function(i, e){
        f_array.push(maptoPNG(e.id));
      });
      Promise.all(f_array).then(() => {
        setTimeout(() => {

          $("#pdf_infos") && $("#pdf_details").html("Création du fichier PDF")

          toPDF(id_element)
          .then(() => {
            $("#pdf_infos") && $("#pdf_details").html("Terminé. Vous pouvez télécharger le pdf")

            $(leaflet_map_selector).show();
            $(leaflet_hide_selector).show();
            $(leaflet_map_selector).each(function(i, e){

              M[e.id].invalidateSize();
              var next=$(e).next()
              if (next.is('img')) {
                next.remove();
              }
            });
            resolve();
            $("#pdf_infos") && $("#pdf_infos").hide()
            cpt_map = 0;
          });
        }, 100)
      });
    });

  }

  M.toPDF_map = toPDF_map;
  M.toPDF = toPDF;

});
