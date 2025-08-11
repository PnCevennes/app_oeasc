import { round } from "@/core/js/util/util.js";
import {localisationTitle, dataTxt } from './util.js'

/**
 * Génère les options de configuration pour un graphique ICE (Indice de Capture par Effort).
 * Utilisé pour afficher l'évolution de l'ICE d'une espèce sur plusieurs saisons, avec intervalles de confiance et tendance.
 * 
 * @param {Object} data - Données statistiques à afficher, incluant les valeurs ICE, intervalles, régression, etc.
 * @returns {Object} chartOptions - Objet de configuration pour un composant graphique (ex: Highcharts, ApexCharts).
 * 
 * Utilisation typique : 
 *   - Dans un composant VueJS affichant un graphique d'effort de capture.
 *   - Appelé lors du rendu ou de la mise à jour des données du graphique.
 */
export default ( data ) => {
  // Extraction des données principales pour le graphique
  const dataGraph = data.res_lm_moy;
  // Récupération des libellés dynamiques selon le type de données (ex: CPUE, effort, etc.)
  const { dataTypeAxis, dataTypeTitle, dataTypeSerie } = dataTxt(data);

  // Options de configuration du graphique
  const chartOptions = {
    // Titre principal du graphique, construit dynamiquement selon les données et la localisation
    title: {
      text: `Evolution des ICE - ${dataTypeTitle} - ${data.nom_espece}${localisationTitle(data)}`
      // localisationTitle(data) ajoute des informations de localisation si disponibles (ex: secteur, plan d'eau)
    },
    // Configuration de l'axe des X (saisons de pêche)
    xAxis: {
      title: {
        text: "Saison"
      },
      labels: {
        enabled: true,
        // Affiche les saisons sous forme "année-année+1" (ex: 2020-2021)
        formatter: function() {
          return `${this.value}-${this.value + 1}`;
        }
      }
    },
    // Configuration de l'axe des Y (valeur de l'ICE ou autre indicateur)
    yAxis: {
      // min, endOnTick, startOnTick peuvent être décommentés pour ajuster l'affichage si besoin
      title: {
        text: dataTypeAxis // Libellé dynamique selon le type de données (ex: "ICE (kg/ha/jour)")
      }
    },
    // Définition des séries de données à afficher sur le graphique
    series: [
      {
        // Série principale : valeurs de l'ICE par saison
        id: "ice",
        name: dataTypeSerie, // Nom dynamique selon le type de données (ex: "ICE moyen")
        lineWidth : 0, // Pas de ligne, points seuls (scatter plot)
        data: Object.keys(dataGraph.x).map(ind => [
          dataGraph.x[ind], // Saison (année)
          dataGraph.y[ind]  // Valeur ICE pour cette saison
        ])
      },
      {
        // Série d'intervalle de confiance (barres d'erreur autour des points ICE)
        type: "errorbar",
        linkedTo: "ice", // Lie cette série à la série principale pour affichage groupé
        name: "Intervalle de confiance",
        data: Object.keys(dataGraph.x).map(ind => [
          dataGraph.x[ind],    // Saison (année)
          dataGraph.inf[ind],  // Borne inférieure de l'intervalle de confiance
          dataGraph.sup[ind]   // Borne supérieure de l'intervalle de confiance
        ]),
        enableMouseTracking: false, // Pas d'interaction souris sur les barres d'erreur
        maxPointWidth: 40 // Largeur max des barres d'erreur
      },
      {
        // Série de régression linéaire (tendance de l'ICE sur la période)
        name: `Regression (p-value=${round(dataGraph.p_value_slope, 3)})`,
        // Style de la ligne selon la significativité statistique de la pente
        dashStyle: dataGraph.p_value_slope < 0.05
          ? 'Solid'      // Ligne pleine si significatif (p < 0.05)
          : 'ShortDash'  // Pointillés sinon
        ,
        // Épaisseur de la ligne selon la p-value (plus épais si tendance marquée)
        lineWidth : dataGraph.p_value_slope <= 0.1
          ? 2 // Plus épais si p-value <= 0.1 (tendance forte ou modérée)
          : 0 // Sinon invisible (pas de tendance)
        ,
        // Deux points pour tracer la droite de régression entre la première et la dernière saison
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
        enableMouseTracking: false, // Pas d'interaction souris sur la tendance
        maxPointWidth: 40
      }
    ],
    // Dimensions du graphique (peuvent être adaptées selon le contexte d'affichage)
    height: "600px",
    width: "600px"
  };
  // Retourne l'objet de configuration à utiliser dans le composant graphique
  return chartOptions;
};
