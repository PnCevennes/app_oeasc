export default (data, { bracelet }) => {
  // const categories = ['CEM', "CEFF", 'CEFFD'].filter;
  // const dataRealise= categories.map(categorie => [categorie, data[categorie].taux_realisation]);
  // const dataNonRealise= categories.map(categorie => [categorie, 100 - data[categorie].taux_realisation]);
  const chartOptions = {
    title: {
      text: `Proportion attribution / réalisation (${bracelet})`
    },
    stacking: true,
    xAxis: {
      // labels: {
      //   enabled: true,
      //   formatter: function() {
      //     return (
      //       data.nb_realisation[this.value][0]
      //     );
      //   }
      // }
    },
    yAxis: {
      // min: -0.01,
      // endOnTick: false,
      // startOnTick: false,
      title: {
        text: "Réalisation"
      }
    },
    plotOptions: {
      pie : {
        dataLabels: {
          enabled: true,
          // distance: -30
        }
      }
    },
    series: [
      {
        name: "%",
        type: "pie",
        data: [
          [
            `Réalisé: ${data[bracelet].nb_realisation} (${data[bracelet].taux_realisation}%)`,
            data[bracelet]["taux_realisation"]
          ],
          [
            `Non Réalisé: ${data[
              bracelet
            ].nb_attribution - data[bracelet].nb_realisation} (${100 - data[bracelet].taux_realisation}%)`,
            100 - data[bracelet]["taux_realisation"]
          ]
        ]
      }
    ],
    height: "600px",
    width: "600px"
  };
  return chartOptions;
};
