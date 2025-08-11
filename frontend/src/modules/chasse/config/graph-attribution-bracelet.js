/**
 * Génère les options de configuration pour un graphique en secteurs (pie chart)
 * représentant la proportion d'attribution et de réalisation pour un type de bracelet donné.
 *
 * @function
 * @param {Object} data - Objet contenant les données statistiques par type de bracelet.
 *   Exemple de structure attendue :
 *   {
 *     [bracelet]: {
 *       nb_realisation: number, // Nombre de réalisations pour ce bracelet
 *       nb_attribution: number, // Nombre total d'attributions pour ce bracelet
 *       taux_realisation: number // Taux de réalisation (en pourcentage) pour ce bracelet
 *     },
 *     ...
 *   }
 * @param {Object} options - Options supplémentaires pour la configuration.
 * @param {string} options.bracelet - Le type de bracelet à afficher dans le graphique.
 * @returns {Object} chartOptions - Objet de configuration pour un composant graphique (ex: Highcharts, ECharts).
 *
 * @example
 * // Utilisation typique dans un composant Vue.js pour afficher un graphique de réalisation :
 * const chartOptions = getChartOptions(data, { bracelet: 'CEM' });
 * // chartOptions peut ensuite être passé à un composant graphique.
 *
 * @description
 * Cette fonction est utilisée dans le module "chasse" pour visualiser, sous forme de graphique circulaire,
 * la proportion de bracelets réalisés par rapport au nombre total attribué pour un type de bracelet donné.
 * Elle est utile pour le suivi des performances ou la visualisation rapide des taux de réalisation.
 */
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
