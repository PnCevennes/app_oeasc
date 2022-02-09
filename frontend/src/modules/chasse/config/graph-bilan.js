import { localisationTitle } from './util.js'
export default ( data ) => {
  const chartOptions = {
      title: {
        text: `Évolution des plans de chasse - ${data.nom_espece}${localisationTitle(data)}.`
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
      tooltip: {
        xDateFormat: '%d/%m/%Y',
        shared: true,
        split: false,
        enabled: true
      },
      series: [
        {
          type: "column",
          name: "Affectation min",
          data: data.nb_attribution_min,
        },
        {
          type: "column",
          name: "Affectation max",
          data: data.nb_attribution_max,
        },
        {
          name: "Réalisations avant novembre",
          data: data.nb_realisation_avant_11,
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
