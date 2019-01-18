$(document).ready(function() {

  "use strict";

  var color_selected = 'rgba(255, 165, 0)';
  var color_not_selected = 'rgb(222, 226, 230);';

  // option du tableau
  var table_indices = {};
  $("thead th").each( (i,e) => table_indices[$(e).html()]=i );
  var table = $("#table_declarations").DataTable({
    columnDefs: [{
      "targets": [ table_indices['ID'] ],
      "width": "30px",
    }, {
      "targets": [ table_indices['Commune(s)'], table_indices['Nom forêt'] ],
      "width": "100px",
    }],

    // searching: false,
    scrollY:  "400px",
    scrollX: true,
    // scrollCollapse: true,
    // scroller:       true,
    paging: false,
    mark: true,
    language: { "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"},
    dom: 'Bfrtip',
    buttons: [
    {
      extend: 'colvis',
      columns: ':not(.noVis)',
      text: 'Choisir les informations à afficher'
    },
    {
      extend: 'csv',
      text: 'Exporter au format CSV'
    }
    ]
    // rowGroup: {
    //   dataSrc: 'group'
    // },

  });


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


  $(document).on("marker_click", function(e, id_declaration){
  /* sélection sur carte: click sur les markers
  */
  var table_filtered = table.rows( { filter : 'applied'} ).data()

  table_filtered.each(function(e,i){

    if( parseInt(e[table_indices['ID']]) == id_declaration) {
      if($('#table_declarations tbody tr').eq(i).hasClass("tr-selected")) {
        $('#table_declarations tbody tr').eq(i).removeClass("tr-selected");
      } else {
        $('.dataTables_scrollBody').animate({
          scrollTop: $('#table_declarations tbody tr').eq(i).offset().top - $('#table_declarations tbody tr').eq(0).offset().top
        }, 800);
        $('#table_declarations tbody tr').eq(i).addClass("tr-selected");
      }

    } else {
      $('#table_declarations tbody tr').eq(i).removeClass("tr-selected");
    }
  })
});


  $('#table_declarations tbody tr').on('click', function() {
    /* sélection sru tableau: click sur les tr
    */
    var $this = $(this);

    $('#table_declarations tbody tr').removeClass( "tr-selected" );

    if($this.hasClass("tr-selected") ) {
      $this.removeClass( "tr-selected" );
      M.markers.eachLayer(function(l){
        if(l.id_declaration == id_declaration) {
          l.closePopup();
        }
      });

    } else {
      $this.addClass("tr-selected");
      var index = $this.index();
      var table_filtered = table.rows( { filter : 'applied'} ).data()
      var id_declaration = parseInt(table_filtered[index][0]);
      M.markers.eachLayer(function(l){
        if(l.id_declaration == id_declaration) {
          l.openPopup();
        }
      });
    }
  });


  table.on('search.dt', function() {
    /* synchronisation de la carte avec les filtres du tableau
    */

    var table_filtered = table.rows( { filter : 'applied'} ).data()
    var v_filtered = [];

    table_filtered.each(function(e){
      var id_declaration = parseInt(e[table_indices['ID']])
      v_filtered.push(id_declaration);
    });

    if(!M.markers_save) {
      M.markers_save = [];
    }

    if( M.markers && M.markers._layers) {
      // on place tous les markers affichés dans un tableau de sauvegarde
      M.markers.getLayers().forEach(function(e) {
        M.markers_save.push(e);
        M.markers.removeLayer(e);
      });

      // on place dans le cluster les marker correspondant au filtrage du tableau
      M.markers_save.forEach(function(e) {
        if(v_filtered.includes(parseInt(e.id_declaration))) {
          M.markers.addLayer(e);
        }
      });

    }
  });

  var set_columns = function(columns_selected) {
    /* Choix des colonnes du tableau
    */
    table.listen_visibility = false;

    if($('#column_search')){
      $('#column_search').remove();
    }

    for(var i=0; i<table.columns()[0].length; i++) {
      // table.column(i).settings()[0].aoColumns[i].bVisible=false;
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
    if($('#table_declarations_filter input').val()==''){
      table.search('wouplaboum').draw();
      table.search('').draw();
    }

    $("#tableau_declarations table").width("100%");
    $("#tableau_declarations table").resize()
    $("#tableau_declarations table thead input").width("100%")
    // $('#table_declarations_filter').val('');
  };

  var selection_tout = []
  for(var i = 0; i < table.columns()[0].length; i++) {
    if(i!=1) {
      selection_tout.push(i);
    }
  }


  var selection_reduite = [0, 2, 3, 4, 5, 11];

  $("[data-type=T]").click(function () {
    /* Onglet tableau
    */
    $("#show_declarations").hide();
    $("#show_declarations").attr("class", "");
    $("#tableau_declarations").show();
    $("#tableau_declarations").attr("class", "col-md-12");
    set_columns(selection_tout);

  });



  $("[data-type=TC]").click(function () {
    /* Onglet tableau + carte
    */
    $("#show_declarations").show();
    $("#show_declarations").attr("class", "col-md-6");;
    $("#tableau_declarations").show();
    $("#tableau_declarations").attr("class", "col-md-6");;
    setTimeout(function(){
      set_columns(selection_reduite);
      $('#map_show_declarations').height($('#tableau_declarations').height());
      M['map_show_declarations'].invalidateSize();
    }, 50);

  });

  // init
  setTimeout(function() {
    $("[data-type=T]").click();
  }, 500);

  var declarations = [];

  $(".data-declaration").each(function(){
    var declaration = JSON.parse($(this).attr("data-declaration"));
    declarations.push(declaration);
  });

  //init
  M.initialiser_show_declarations('show_declarations', declarations);

  $(".button-supprimer-declaration").click(function() {
    var $this = $(this);
    var id_declaration = $this.attr('data-id-declaration');
    $.ajax({
      type: 'POST',
      url: "/api/declaration/delete_declaration/" + id_declaration,
    }).done(function(response) {
      console.log("done : " + this.url);
      $this.parents("tr").remove();
    }).fail(function(response) {
      console.log("fail : " + this.url, response);
    });

  });


  var set_tab_declaration = function(id_declaration) {
    /*
    ouvre au besoin une nouvelle tab du tableau pour voir les details d une declaration
    */
    return new Promise((resolve, reject) => {
      var selector='#declarations_tabs a[href$=declaration_' + id_declaration + '_container]'
      var tab_link = $(selector);

      var new_tab=false

      if(tab_link.length) {
        tab_link.click();
        resolve(new_tab);
        return;
      }

      $('#declarations_tabs').append(
        '<a class="nav-item nav-link" href="#declaration_' + id_declaration + '_container" data-toggle="tab" data-type="TC">\
        Déclaration ' + id_declaration + '<button class="close closeTab" type="button" >×</button></a>');

      $(selector + ' button').click(function(e) {
        e.preventDefault();

        if($(this).parent().hasClass("active")) {
          var prev = $(this).parent().prev()
          prev.tab("show");
          console.log("aa", prev);

        }
        var id=$(selector).attr("href");
        $(id).remove();
        setTimeout(()=>$(selector).remove(), 10);
      });

      $('#declarations').append('<div class="tab-pane active" id="declaration_' + id_declaration + '_container">Chargement en cours</div>')
      $.ajax('/api/declaration/declaration_html/' + id_declaration + '?btn_action=1')
      .done((response) => {
        $('#declaration_' + id_declaration +"_container").html(response);
        $('[data-toggle="tooltip"]').tooltip();
        var declaration = JSON.parse($('#declaration_' + id_declaration).attr("data-declaration"));
        /*
        TODO + centroid
        */
        // if(! M["map_show_localisation_" + id_declaration] && declaration) {
        //   setTimeout(function() { M.initialiser_show_localisation("show_localisation_" + id_declaration, declaration); }, 10);
        // }

        new_tab=true;
        resolve(new_tab)})
      .fail((response) => {$('#declaration_'+id_declaration).html("<div>Fail</div>" + response)});

      $(selector).tab("show");
    });
  };

  var declaration2pdf = function(id_declaration) {
    /*
    pour faire le pdf d 'une déclaration'
    */
    var selector='#declarations_tabs a[href$=declaration_' + id_declaration + '_container]'
    set_tab_declaration(id_declaration).then(function(new_tab) {
      M.toPDF_map("declaration_" + id_declaration).then(function(){
        new_tab && $(selector + ' button').click();
      });
    });

  }

  M.set_tab_declaration = set_tab_declaration;
  M.declaration2pdf = declaration2pdf;

});
