$(document).ready(function() {

  "use strict";


  // option du tableau

  var table = $("#table_declarations").DataTable({
    columnDefs: [
    {
      "targets": [ 0 ],
      "visible": false,
      "searchable": false,
    },
    ],

    scrollY:  "400px",
    scrollCollapse: true,
    // scroller:       true,
    paging: false,
    mark: true,
    language: { "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"},
    dom: 'Bfrtip',
    buttons: [
    {
      extend: 'colvis',
      columns: ':not(.noVis)',
    },
    'csv'
    ]
    // rowGroup: {
    //   dataSrc: 'group'
    // },

  });

  M.listen_visibility = false;

  M.table = table;

  var init_column_search = function() {

    table.listen_visibility = false;

    if($('#column_search')){

      $('#column_search').remove();

    }

    $('.dataTables_scrollHead thead').append("<tr id='column_search'></tr>");

    $('.dataTables_scrollHead thead th').each( function () {
      var title = $(this).text();
      $('#column_search').append( '<th><input type="text" placeholder="'+title+'" /></th>' );
    } );


    var cols_search = $('#column_search input')

    var visible_columns = [];
    var ind_visible_columns = [];

    for(var i = 0; i < table.columns().visible().length; i++ ) {

      if(table.columns().visible()[i]) {

        var col = table.column(i)
        visible_columns.push(col);
        ind_visible_columns.push(i);

      }

    }


    for(var i=0; i < cols_search.length; i++) {

      var col_search = cols_search[i];
      $(col_search).width(10);

      var w = $($("#tableau_declarations td")[i]).width();
      $(col_search).width(w-20);

    }

    visible_columns.forEach(function(e) {

      var title = $(e.header()).html();
      var input = $("[placeholder='" + title + "'");

      $(input).on( 'keyup change', function () {

        if ( e.search() !== this.value ) {

          e
          .search( this.value )
          .draw();

        }

      });


    });

    table.listen_visibility=true;

  };


  table.on('column-visibility', function() {

    if(table.listen_visibility) {

      init_column_search();
      
    }

  });


// survol des markers

$(document).on("marker_mouseover", function(e, id_declaration){


  var table_filtered = table.rows( { filter : 'applied'} ).data()

  table_filtered.each(function(e,i){

    if( parseInt(e[0]) == id_declaration) {

      $('.dataTables_scrollBody').animate({
        // scrollTop: $('#table_declarations tbody tr').eq(i).offset().top - $('.dataTables_scrollBody').offset().top
        scrollTop: $('#table_declarations tbody tr').eq(i).offset().top - $('#table_declarations tbody tr').eq(0).offset().top
      }, 800);

      console.log($('#table_declarations tbody tr').eq(i).offset().top, $('.dataTables_scrollBody').offset().top);
      console.log($('#table_declarations tbody tr').eq(i).offset().top - $('.dataTables_scrollBody').offset().top);
      $('#table_declarations tbody tr').eq(i).css( "background-color", "Orange" );

    }

  })

});

$(document).on("marker_mouseout", function(e, id_declaration){

  var table_filtered = table.rows( { filter : 'applied'} ).data()

  table_filtered.each(function(e,i){

    if( parseInt(e[0]) == id_declaration) {
      $('#table_declarations tbody tr').eq(i).css( "background-color", "" );

      // $('#table_declarations tbody tr').eq(i).removeClass('row-selected');

    }

  })

});


$('#table_declarations tbody tr').on('mouseover', function() {

  $(this).css( "background-color", "Orange" );

  var index = $(this).index();

  var table_filtered = table.rows( { filter : 'applied'} ).data()

  var id_declaration = parseInt(table_filtered[index][0]);

  M.markers.eachLayer(function(l){

    l.closePopup()

    if(l.id_declaration == id_declaration) {

      // console.log("a");
      M.markers.zoomToShowLayer(l, function(){l.openPopup()});
      // l.openPopup();
// M.markers.disableClusteringAtZoom=1;
    }

  });

});


$('#table_declarations tbody tr').on('mouseout', function() {

  $(this).css( "background-color", "" );

  var index = $(this).index();

  var table_filtered = table.rows( { filter : 'applied'} ).data()

  var id_declaration = parseInt(table_filtered[index][0]);

// M.markers.zoomToBounds();

  M.markers.eachLayer(function(l){

    l.closePopup();

  });

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

  var set_columns = function(columns_selected) {

    table.listen_visibility = false;

    if($('#column_search')){

      $('#column_search').remove();

    }

    for(var i=0; i<table.columns()[0].length; i++) {

      table.column(i).visible(false);
      table.column(i).settings()[0].aoColumns[i].bSearchable = false;

    }

    for (var i=0; i<columns_selected.length; i++) {

      var ind = columns_selected[i];
      table.column(ind).visible(true);
      table.column(ind).settings()[0].aoColumns[i].bSearchable = true;

    }

    table.listen_visibility = true;

    init_column_search();

  };


  var selection_tout = []
  for(var i = 1; i < table.columns()[0].length; i++) {

    selection_tout.push(i);

  }

  var selection_reduite = [1, 3, 4, 8, 9, 10, 11];

  $("[data-type=T]").click(function () {

    $("#show_declarations").hide();
    $("#show_declarations").attr("class", "");
    $("#tableau_declarations").show();
    $("#tableau_declarations").attr("class", "col-md-12");

    set_columns(selection_tout);


  });

  $("[data-type=C]").click(function () {

    $("#tableau_declarations").hide();
    $("#tableau_declarations").attr("class", "");
    $("#show_declarations").show();
    $("#show_declarations").attr("class", "col-md-12");

    setTimeout(function(){ M['map_show_declarations'].invalidateSize()}, 100);

  });


  $("[data-type=TC]").click(function () {

    $("#show_declarations").show();
    $("#show_declarations").attr("class", "col-md-6");;
    $("#tableau_declarations").show();
    $("#tableau_declarations").attr("class", "col-md-6");;

    setTimeout(function(){

      M['map_show_declarations'].invalidateSize();
      set_columns(selection_reduite);

    }, 100);


  });

    // init

    setTimeout(function() {

      set_columns(selection_reduite)
      $("#map_show_declarations").height($("#tableau_declarations").height());
      setTimeout(function(){ M['map_show_declarations'].invalidateSize(); init_column_search()}, 100);
      // init_column_search();

    }, 400);





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
