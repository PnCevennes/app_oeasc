var makeScale = (chartOptions, options) => {
  switch (options.type) {
    case "bar":
      chartOptions.options.scales = {
        xAxes: [
          {
            ticks: {
              display: false //this will remove only the label
            }
          }
        ],
        yAxes: [
          {
            ticks: {
              beginAtZero: true
            }
          }
        ]
      };
      break;
  }
  switch (options.util) {
    case "time":
        console.log('aa')
      chartOptions.options.scales = {
        xAxes: [
          {
            type: "time",
            time: {
              unit: "month"
            },
            stacked: true
          }
        ],
        yAxes: [
          {
            ticks: {
              beginAtZero: true
            },
            stacked: true
          }
        ]
      };
  }
};

export { makeScale };
