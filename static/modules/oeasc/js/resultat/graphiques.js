$(document).ready(function() {

  G = {};

  "use strict";

  var init_timeline = function(id) {
    $.ajax('/api/resultat/timeline').done(function(response) {
      var ctx = document.getElementById(id).getContext('2d');
      var dchart = {
        type: 'bar',
        data: response.data,
        options: {
          locale: 'fr',
          title: {
            display: true,
            text: "Titre",
          },
          responsive:true,
          maintainAspectRatio:false,
          scales: {
            xAxes: [{
              type: 'time',
              scaleLabel: {
                display: true,
                labelString: 'Date',
              }
            }],
            yAxes: [{
              scaleLabel: {
                display: true,
                labelString: 'value',
              },
              ticks:{
                suggestedMin: 0,
              },
            }]
          },
        }
      };
      var myChart = new Chart(ctx, dchart);
    });
  };


  $('.chart').each(function(e){
      var $this=$(this);
      var id = $this.attr("id");
      if($this.hasClass("timeline")) {
        init_timeline(id);
      };
    });

});
