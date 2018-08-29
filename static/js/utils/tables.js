$(document).ready(function() {
  // Setup - add a text input to each footer cell
  $.extend(true, $.fn.dataTable.defaults, {

    mark: true,
    "language": {
      "url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/French.json"
    },
    initComplete: function () {
      var that = this;
      var s = "";
      var n=1;
      var thead=this.find("thead");

      thead.find("th").each( function (ind){s +='<td class="select_' + ind + '"><select><option value=""></option></select></td>'});
      thead.prepend($('<tr class="combobox-row">'+s+'</tr>'))
      this.api().columns().every( function () {
        var column = this;
        select = $(".select_" + column.index() + " select")
        .on( 'change', function () {
          var val = $.fn.dataTable.util.escapeRegex(
            $(this).val()
            );

          column
          .search( val ? '^'+val+'$' : '', true, false )
          .draw();
        } );

        column.data().unique().sort().each( function ( d, j ) {

          if( d != null ) { 
            if( d != "" ) {
              select.append( '<option value="'+d+'">'+d+'</option>' )
            }
          }
        } );
      } );
      this.on( 'change', function () {

        that.api().columns().every( function () {
          var column = this;

// ;        select = $(".select_" + column.index() + " select");
//         column.data({search:'applied'}).unique().sort().each( function ( d, j ) {
//           select.append( '<option value="'+d+'">'+d+'</option>' )
        // } );
      } );
      } );
    }
  } );
} );
