$(document).ready(function() {

  G = {};

  "use strict";

  var dl2ld = function(dl) {
    /*
      passe d'un dictionnaire de liste a une liste dictionnaires
      dl: dictionnaire de liste
      ld: liste de dictionnaire
    */
    var ld = [];
    for( var key in dl) {
      for(var i=0; i<dl[key].length; i++) {
        if(! ld[i]) ld[i]={};
        ld[i][key] = dl[key][i];
      }
    }
    return ld;
  }

  var set_title = function(svg, title) {

    svg.append("text")
      .attr('fill', 'black')
      .attr("x", (svg.width + svg.margin.left + svg.margin.right) / 2)
      .attr("y", (svg.height + svg.margin.top + svg.margin.bottom) - 30)
      .attr("text-anchor", "middle")
      .attr("with", (svg.width + svg.margin.left + svg.margin.right) * 0.8)
      .style("font-size", "18px")
      .style("text-decoration", "underline")
      .text(title);


  }

  var set_axes = function(svg, data) {
    /*
      axes
    */
    svg.x = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([svg.margin.left, svg.margin.left + svg.width])
    var xAxis = g => g
      .attr("transform", `translate(0,${svg.height + svg.margin.top})`)
      .call(d3.axisBottom(svg.x).ticks(svg.width / 80))
      // .call(g => g.select(".domain").remove());
    svg.append("g")
      .call(xAxis);

    svg.y = d3.scaleBand()
      .domain(data.map(d => d.mnemo))
      .range([svg.height + svg.margin.top, svg.margin.top])
      .padding(0.1)
    var yAxis = g => g
      .attr("transform", `translate(${svg.margin.left},0)`)
      .call(d3.axisLeft(svg.y).tickSizeOuter(0))
    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  }

  var set_data_rect = function(svg, data) {

    svg.append("g")
    .selectAll("rect")
    .data(data)
    .enter().append("rect")
    .attr('class', "bars")
    .attr("fill", "blue")
    .attr("width", 0)
    .attr("height", svg.y.bandwidth())
    .attr("y", d => svg.y(d.mnemo) )
    .attr("x", svg.x(0))
    .attr("width", d => svg.x(d.value) - svg.x(0) )

  }

  var init_graph = function(data_in, id, title) {
    /*
      Fonction pour créer les graphiques
    */

    const svg = d3.select('#' + id);

    var data = dl2ld(data_in)

    svg.margin = {top: 100, right: 100, bottom: 100, left: 100}
    svg.height = 200;
    svg.width = 1.618 * svg.height;

    svg.style('height', svg.height + svg.margin.top + svg.margin.top + 'px')
    svg.style('width', svg.width + svg.margin.left + svg.margin.right + 'px')
    svg.style('background-color', 'lightgray')

    set_title(svg, title)
    set_axes(svg, data);
    set_data_rect(svg, data);

  }

  var graph = function(id, title) {
    /*
      initie un graph à partir d'une url
    */
    url = '/api/resultat/test';
    $.ajax(url).done(function(data){
      init_graph(data, id, title);
    }).fail(function(data){
      console.log("fail", data);
    });

  }

  var set_graphs = function() {
  /*
    init les div de class graph
  */
    $('.graph').each(function() {
      var $this = $(this);
      var title = $this.attr('title');
      var id = $this.attr('id');
      var id_graph = "graph_" + id;
      $this.append("<svg id='" + id_graph + "'></svg>")
      graph(id_graph, title)
    });
  }

  G.init_graph = init_graph;
  G.graph = graph;
  G.set_graphs = set_graphs

});
