export default ( data ) => {
  let names = data.nom_espece
  for (const key of ['nom_zone_indicative', 'nom_zone_cynegetique'].filter(k => !!data[k])) {
    names += `, ${data[key]}`
    break;
  }
  const chartOptions = {
      title: {
        text: `Évolution des plans de chasse : ${names}.`
      },
      xAxis: {
        title: {
          text: "Saisons"
        },
        labels: {
          enabled: true,
          formatter: function() {
            return (
              data.nb_realisation[this.value][0]
            );
          }
        }
      },
      yAxis: {
        // min: -0.01,
        // endOnTick: false,
        // startOnTick: false,
        title: {
          text: "Réalisation"
        }
      },
      series: [
        {
          type: "column",
          name: "Affectation min",
          data: data.nb_attribution_min
        },
        {
          type: "column",
          name: "Affectation max",
          data: data.nb_attribution_max
        },
        {
          name: "Réalisations avant novembre",
          data: data.nb_realisation_avant_11
        },
        {
          name: "Réalisations",
          data: data.nb_realisation
        }
      ],
      height: "600px",
      width: "600px"
  };
  return chartOptions;
};
