"use strict";

var init_bar_chart = function(response, name, names_origin) {

  var data = response.data;

  var nb_alertes = response.nb_alertes;

  console.log(nb_alertes, response)

  var width = 1000;

  var margin = ({top: 70, right: 170, bottom: 100, left: 70})

  var height = data.length * 25 + margin.top + margin.bottom

  var d_max = d3.max(data, d => d.value)

  var x = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)])
  .range([margin.left, width - margin.right])


  var x2 = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)/nb_alertes])
  .range([margin.left, width - margin.right])


  var y = d3.scaleBand()
  .domain(data.map(d => d.name))
  .range([margin.top, height - margin.bottom])
  .padding(0.1)

  var y_legend = d3.scaleBand()
  .domain(names_origin)
  .range([margin.top, height - margin.bottom])
  .padding(0.1)



  var yAxis = g => g
  .attr("transform", `translate(${margin.left},0)`)
  .call(d3.axisLeft(y).tickSizeOuter(0))

  var xAxis = g => g
  .attr("transform", `translate(0,${margin.top})`)
  .call(d3.axisTop(x).ticks(width / 80))
  .call(g => g.select(".domain").remove());

  var format2 = d3.format(".1f");


  var xAxis2 = g => g
  .attr("transform", `translate(0, ${height - margin.bottom})`)
  .call(d3.axisBottom(x2).ticks(width / 80).tickFormat(d3.format(".0%")))
  .call(g => g.select(".domain").remove())


  var format = d3.format(".0f");

  var div = d3.select("body").append("div")
  .attr("class", "tooltip")
  .style("opacity", 0);


  const svg = d3.select('.chart');

  svg.style('background-color', 'lightgray')

  // rect
  // svg.append("g")
  // .attr("fill", "steelblue")
  // .selectAll("rect")
  // .data(data)
  // .enter().append("rect")
  // .attr("x", x(0))
  // .attr("y", d => y(d.name))

  // .attr("width", 0).
  // transition().duration(1000).delay(function(d,i){return (100*i);})
  // .attr("width", d => x(d.value) - x(0))
  // .attr("height", y.bandwidth());


  var color = ['red', 'orange', 'yellow'];

  for (var ind in names_origin) {

    var name = names_origin[ind];

    svg.append("g")
    .selectAll("rect")
    .data(data)
    .enter().append("rect")
    .attr('class', "bars")
    .attr("fill", color[ind])
    .attr("width", 0)
    .attr("height", y.bandwidth())
    .attr("y", function(d) { return y(d.name) } )
    .attr("x", x(0))
    .transition()
    .duration(1000)
    .attr("x", function(d) { var dec = 0; for(var j=0; j<ind; j++) {dec += d.values_origin[names_origin[j]]}; return x(dec);})
    .attr("width", d => x(d.values_origin[name]) - x(0) )

    svg.append("g")
    .attr("fill", "black")
    .attr("text-anchor", "end")
    .style("font", "12px sans-serif")
    .selectAll("text")
    .data(data)
    .enter().append("text")
    .attr('class', "bars-text")
    .attr("x", x(0))
    .attr("y", d => y(d.name) + y.bandwidth() / 2)
    .attr("dy", "0.35em")
    .style("opacity", 0)
    .transition()
    .duration(1000)
    .style("opacity", 1)
    .attr("x", function(d) { var dec = 0; for(var j=0; j<ind; j++) {dec += d.values_origin[names_origin[j]]}; return x(dec + d.values_origin[name]) - 4})
    .text(d => format(d.values_origin[names_origin[ind]]));

  }

  svg.append("g")
  .attr("fill", "black")
  .attr("text-anchor", "start")
  .style("font", "15px bold sans-serif")
  .selectAll("text")
  .data(data)
  .enter().append("text")
  .attr('class', "bars-text")
  .attr("x", x(0))
  .attr("y", d => y(d.name) + y.bandwidth() / 2)
  .attr("dy", "0.35em")
  .style("opacity", 0)
  .transition()
  .duration(1000)
  .style("opacity", 1)
  .attr("x", d => x(d.value) + 4)
  .text(d => format(d.value));



  svg.append("g")
  .selectAll("rect")
  .data(names_origin)
  .enter().append('rect')
  .attr("fill", function(d, i) {return color[i]})
  .attr('x', width - margin.right + 20)
  .attr('y', d => y_legend(d))
  .attr("height", y.bandwidth())
  .attr("width", 20)

  svg.append("g")
  .attr("fill", "black")
  .attr("text-anchor", "begin")
  .style("font", "12px sans-serif")
  .selectAll("text")
  .data(names_origin)
  .enter().append('text')
  .attr("fill", 'black')
  .attr('x', width - margin.right + 50)
  .attr('y', d => y_legend(d)  + y.bandwidth() / 2)
  .attr("dy", "0.35em")
  .text(d => d)
  .on("click", function() {
    name = $(this).html(); data.sort((a, b) => a.values_origin[name] - b.values_origin[name]); for(var d in data) console.log(data[d]);

    var y = d3.scaleBand()
    .domain(data.map(d => d.name))
    .range([margin.top, height - margin.bottom])
    .padding(0.1)

    d3.selectAll('.bars').transition().duration(1000)
    .attr("y", d => y(d.name))
    d3.selectAll('.bars-text').transition().duration(1000)
    .attr("y", d => y(d.name)  + y.bandwidth() / 2)
      // .attr("y", d => 0)
      ;

      var yAxis = g => g
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y).tickSizeOuter(0))

 d3.select(".y.axis") // change the y axis
 .transition()
 .duration(1000)
 .call(yAxis);

});



// text
// svg.append("g")
// .attr("fill", "white")
// .attr("text-anchor", "end")
// .style("font", "12px sans-serif")
// .selectAll("text")
// .data(data)
// .enter().append("text")
// .attr("x", d => x(d.value) - 4)
// .attr("y", d => y(d.name) + y.bandwidth() / 2)
// .attr("dy", "0.35em")
// .text(d => format(d.value));

svg.append("g")
.call(xAxis);

svg.append("g")
.call(xAxis2);


svg.append("g")
.attr("class", "y axis")
.call(yAxis);

svg
.append("text")
.attr('fill', 'black')
.attr("x", (width / 2))
.attr("y", height - 30)
.attr("text-anchor", "middle")
.style("font-size", "18px")
.style("text-decoration", "underline")
.text("Histogramme des différents types de dégâts avec répartition par orgine de peuplement");

      // text label for the y axis
      svg.append("text")
      .style("font-size", "12px")
      .attr("transform", "rotate(-90)")
      .attr("y", 10 )
      .attr("x",0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text("Type de dégât");

  // text label for the x axis
  svg.append("text")
  .style("font-size", "12px")
  .attr('x', x(d_max/2))
  .attr("transform",
    "translate(" + (0 * width/2) + " ," +
    (height - margin.bottom + 40) + ")")
  .style("text-anchor", "middle")
  .text("Pourcentage");


  // text label for the x axis
  svg.append("text")
  .style("font-size", "12px")
  .attr('x', x(d_max/2))
  .attr("transform",
    "translate(" + (0 * width/2) + " ," +
    (margin.top -30) + ")")
  .style("text-anchor", "middle")
  .text("Nombre (pour un total de " + nb_alertes + " alertes)");


  svg.style('height',height + 'px')
  svg.style('width',width + 'px')

  d3.selectAll('.y .tick text').on('mouseover',function(){

    var name = $(this).html();
    var label = data.filter(d => d.name == name)[0].label
    var position = $(this).offset();
    console.log("aa",label);

      // position.left += 20;
      position.top -= 40;

      $(this).attr('fill', 'red');
      $("div.tooltip").css(position);
      $("div.tooltip").html(label);
      div.transition().duration(500).style("opacity", 0.9);
    });
  d3.selectAll('.y .tick text').on('mouseout',function(){
    div.transition().duration(500).style("opacity", 0);
    $(this).attr('fill', 'black');

  });

}

$.ajax('/api/declaration/declarations')
.done(function(response){

  console.log(response);
  var declarations = response


  var dict_data = {}
  var names_origin = []
  var nb_alertes = declarations.length;

  declarations.forEach(function(declaration){

    var nomenclature_type = 'id_nomenclature_peuplement_origine'

    var origine_peuplement = declaration[nomenclature_type]
    var origine_peuplement_name = declaration[nomenclature_type]['mnemonique']


    var degats = declaration['degats']

    degats.forEach(function(degat){

      var degat_type = degat['id_nomenclature_degat_type']
      var name = degat['id_nomenclature_degat_type']['mnemonique']
      var label = degat['id_nomenclature_degat_type']['label_fr']

      if (! dict_data[name]) {

        dict_data[name] = {'name' : name, 'label':label, value: 0, 'values_origin': {}}

      }

      if (! names_origin.includes(origine_peuplement_name)) {

        names_origin.push(origine_peuplement_name);

      }

      if (! dict_data[name]['values_origin'][origine_peuplement_name]) {

        dict_data[name]['values_origin'][origine_peuplement_name] = 0

      }

      dict_data[name]['value'] += 1;
      dict_data[name]['values_origin'][origine_peuplement_name] += 1

    })

  });

  console.log("dict_data", dict_data);

  var data = []

  for( var key in dict_data) {

    data.push(dict_data[key])

  }

  data.sort((a, b) => a.value - b. value);

  console.log(data)

  init_bar_chart({'data': data, 'nb_alertes': nb_alertes}, 'names_origin', names_origin);

});
