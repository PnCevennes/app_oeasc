var barLegend = {
  position: "left",
  labels: {
    generateLabels: function(chart) {
      var labels = chart.data.labels;
      var dataset = chart.data.datasets[0];
      var legend = labels.map(function(label, index) {
        return {
          datasetIndex: 0,
          fillStyle: dataset.backgroundColor && dataset.backgroundColor[index],
          strokeStyle: dataset.borderColor && dataset.borderColor[index],
          lineWidth: dataset.borderWidth,
          text: label
        };
      });
      return legend;
    }
  }
};

var makeLegend = (chartOptions, options) => {
  chartOptions.options.legend = {
    position: "left"
  };
  switch (options.type) {
    case "pie":
      chartOptions.options.legend = {
        position: "left"
      };
      break;
    case "bar":
      if (!options.split) {
        chartOptions.options.legend = barLegend;
      }
      break;
  }
  switch (options.util) {
    case "time":
      console.log(options.split);
      if (!options.split) {
        chartOptions.options.legend = {
          display: false
        };
      }
      break;
  }
};

export { makeLegend };
