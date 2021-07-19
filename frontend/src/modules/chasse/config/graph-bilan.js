export default ( data ) => {
  const chartOptions = {
      title: {
        text: `Évolution des plans de chasse : ${data.nom_espece}, ${data.nom_zone_cynegetique}.`
      },
      xAxis: {
        title: {
          text: "Saisons"
        },
        labels: {
          enabled: true,
          formatter: function() {
            return (
              data.nb_realise[this.value][0]
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
          data: data.nb_affecte_min
        },
        {
          type: "column",
          name: "Affectation max",
          data: data.nb_affecte_max
        },
        {
          name: "Réalisations avant novembre",
          data: data.nb_realise_avant_11
        },
        {
          name: "Réalisations",
          data: data.nb_realise
        }
      ],
      height: "600px",
      width: "600px"
  };
  return chartOptions;
};
