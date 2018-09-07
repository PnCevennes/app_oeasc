$(document).ready(function() {

  "use strict";


  // option du tableau

  var table = $("#table_declarations").DataTable({
    columnDefs: [
    {
      "targets": [ 0 ],
      "visible": false,
      "searchable": false,
      // 'stateSave': true

    }
    ],

    mark: true,
    language: { "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"},
    dom: 'Bfrtip',
    buttons: [
    'copy', 'csv', 'excel', 'pdf', 'print'
    ]
    // rowGroup: {
    //   dataSrc: 'group'
    // },

  });



    // synchronisation de la carte avec les filtres du tableau

    table.on('search.dt', function() {

      var table_filtered = table.rows( { filter : 'applied'} ).data()

      var v_filtered = [];

      table_filtered.each(function(e){

        var id_declaration = parseInt(e[0])

        v_filtered.push(id_declaration);

      });

      if(!M.markers_save) {

        M.markers_save = [];

      }

      if( M.markers) {

      // on place tous les markers affichés dans un tableau de sauvegarde
      M.markers.getLayers().forEach(function(e) {

        M.markers_save.push(e);
        M.markers.removeLayer(e);

      });

      // on place dans le cluster les marker correspondant au filtrage du tableau
      M.markers_save.forEach(function(e) {

        if(v_filtered.indexOf(e.id_declaration) != -1) {

          M.markers.addLayer(e);

        }

      });

    }

  });

    var declarations = [];

    $(".data-declaration").each(function(){

      var declaration = M.get_from_flask_json($(this).attr("data-declaration"));
      declarations.push(declaration);

    });

    M.initialiser_show_declarations('show_declarations', declarations);

    $(".button-supprimer-declaration").click(function() {

      var $this = $(this);
      var id_declaration = $this.attr('data-id-declaration');

      $.ajax({

        type: 'POST',
        url: "/api/oeasc/delete_declaration/" + id_declaration,

      }).done(function(response) {

        console.log("done : " + this.url);
        $this.parents("tr").remove();

      }).fail(function(response) {

        console.log("fail : " + this.url, response);

      });

    });

  });
