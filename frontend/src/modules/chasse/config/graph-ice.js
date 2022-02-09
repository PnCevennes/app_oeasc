import { round } from "@/core/js/util/util.js";

export default ( data ) => {
  const dataGraph = data.res_lm_moy;
  const chartOptions = {
    title: {
      text: `Evolution des ICE - Masse Corporelle - ${data.nom_espece} - ${data.nom_zone_cynegetique || data.nom_secteur}`
    },
    xAxis: {
      title: {
        text: "Saison"
      },
      labels: {
        enabled: true,
        formatter: function() {
          return `${this.value}-${this.value + 1}`;
        }
      }
    },
    yAxis: {
      // min: -0.01,
      // endOnTick: false,
      // startOnTick: false,
      title: {
        text: "Poids (kg)"
      }
    },
    series: [
      {
        id: "ice",
        name: "Poids moyen",
        data: Object.keys(dataGraph.x).map(ind => [
          dataGraph.x[ind],
          dataGraph.y[ind]
        ])
      },
      {
        type: "errorbar",
        linkedTo: "ice",
        name: "Intervalle de confiance",
        data: Object.keys(dataGraph.x).map(ind => [
          dataGraph.x[ind],
          dataGraph.inf[ind],
          dataGraph.sup[ind]
        ]),
        enableMouseTracking: false,
        maxPointWidth: 40
      },
      {
        name: `Regression (p-value=${round(dataGraph.p_value_slope, 3)})`,
        data: [
          [
            dataGraph.x[0],
            dataGraph.intercept + dataGraph.x[0] * dataGraph.slope
          ],
          [
            dataGraph.x[dataGraph.x.length - 1],
            dataGraph.intercept +
              dataGraph.x[dataGraph.x.length - 1] * dataGraph.slope
          ]
        ],
        enableMouseTracking: false,
        maxPointWidth: 40
      }
    ],
    height: "600px",
    width: "600px"
  };
  return chartOptions;
};
