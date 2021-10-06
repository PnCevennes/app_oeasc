export default (data, options, restitution) => {
  const chartOptions = {
    title: {
      text: options.title
    },
    xAxis: {
      categories: data.map(d => `${d.text} (${d.count})`)
    },
    yAxis: {
      // min: -0.01,
      // endOnTick: false,
      // startOnTick: false,
      title: {
        text: "nb"
      }
    },
    series: [
      {
        type: options.typeGraph,
        name: restitution.items[options.field_name].text,
        colorByPoint: true,
        data: data.map(d => ({
          name: `${d.text} (${d.count})`,
          y: d.count,
          color: null
        }))
      }
    ],
    height: "600px",
    width: "600px"
  };
  return chartOptions;
};
