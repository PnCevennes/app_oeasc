import { round } from "@/core/js/util/util.js";
import {localisationTitle } from './util.js'

export default ( data )  => {
  const dataGraph = data.res_lm_data;
  const chartOptions = {
    title: {
      text: `Poids vide / jour - ${data.nom_espece}${localisationTitle(data)}`
    },
    xAxis: {
      title: {
        text: "Jour"
      },
      labels: {
        enabled: true
        // formatter: function() {
        //   return `${this.value}-${this.value + 1}`;
        // }
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
        id: "pv",
        name: "Poids vide",
        lineWidth: 0,
        marker: {
          enabled: true,
          radius: 3
        },
        states: {
            hover: {
                lineWidthPlus: 0
            }
        },
        data: Object.keys(dataGraph.x).map(ind => [
          dataGraph.x[ind],
          dataGraph.y[ind]
        ])
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
        dashStyle: dataGraph.p_value_slope < 0.05
          ? 'Solid'
          : 'ShortDash'
        ,
        lineWidth : dataGraph.p_value_slope <= 0.1
          ? 2
          : 0
        ,
        enableMouseTracking: false,
        maxPointWidth: 40
      }
    ],
    height: "600px",
    width: "600px"
  };
  return chartOptions;
};
