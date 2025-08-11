<template>
  <div>
    <!-- 
      Affiche le graphique si les options du graphique sont définies.
      La hauteur est définie par la prop 'height' ou 400px par défaut.
    -->
    <div
      v-if="chartOptions"
      :style="`height:${height || '400px'}; width: 100%`"
    >
      <!-- 
        Composant Highcharts affiché si le traitement n'est pas en cours.
        Les options et l'instance Highcharts sont passées en props.
      -->
      <highcharts
        v-if="!processing"
        :style="`width:${width || '100%'}; height:${height || '400px'}`"
        :options="chartOptions"
        :highcharts="hcInstance"
      ></highcharts>
      <!-- 
        Affiche une barre de progression si le traitement est en cours.
      -->
      <v-progress-linear v-else active indeterminate></v-progress-linear>
    </div>
    <!-- 
      Snackbar affiché en cas d'erreur, avec un message d'erreur personnalisé.
      Disparaît automatiquement après 5 secondes.
    -->
    <v-snackbar color="error" v-model="bError" :timeout="5000">
      {{ msgError }}
    </v-snackbar>
  </div>
</template>

<script>
import Highcharts from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import processIce from "./config/graph-ice.js";
import processIceData from "./config/graph-ice-data.js";
import processBilan from "./config/graph-bilan.js";
import processAttributionBracelet from "./config/graph-attribution-bracelet.js";

// Initialise le module d'exportation de Highcharts (permet l'export PNG, PDF, etc. depuis le menu du graphique)
exportingInit(Highcharts);
// Initialise le module d'exportation hors-ligne de Highcharts (permet l'export même sans connexion internet)
offlineExporting(Highcharts);

export default {
  name: "graph-chasse",
  props: [
    "id_espece",
    "id_zone_cynegetique",
    "id_secteur", 
    "id_zone_indicative",
    "id_saison",
    "bracelet",
    "type",
    "width",
    "height",
    "poids_ou_dagues"
  ],
  data: () => ({ // Déclaration de la fonction data qui retourne un objet d'état local du composant
    msgError: null, // Message d'erreur à afficher dans le snackbar en cas de problème lors du chargement des données
    bError: null, // Booléen pour contrôler l'affichage du snackbar d'erreur
    chartOptions: null, // Options du graphique Highcharts générées dynamiquement selon les données reçues
    hcInstance: Highcharts, // Instance de Highcharts utilisée par le composant <highcharts>
    processData: { // Objet associant chaque type de graphique à sa fonction de traitement des données
      ice: processIce, // Fonction de traitement pour le type 'ice'
      ice_data: processIceData, // Fonction de traitement pour le type 'ice_data'
      bilan: processBilan, // Fonction de traitement pour le type 'bilan'
      attribution_bracelet: processAttributionBracelet // Fonction de traitement pour le type 'attribution_bracelet'
    },

    actions: { // Objet associant chaque type de graphique à l'action Vuex correspondante pour récupérer les données
      ice: "chasseIce", // Action Vuex pour le type 'ice'
      attribution_bracelet: "chasseAttributionBracelet", // Action Vuex pour le type 'attribution_bracelet'
      ice_data: "chasseIce", // Action Vuex pour le type 'ice_data'
      bilan: "chasseBilan" // Action Vuex pour le type 'bilan'
    },
    processing: false // Booléen indiquant si un traitement (chargement des données) est en cours
  }),
  

  watch: {
    $props: {
      handler() {
        this.process();
      },
      deep: true,
      immediate: true
    }
  },

  
  methods: {

    /**
     * Traite les données pour générer les options du graphique selon les paramètres sélectionnés.
     * 
     * Cette fonction est appelée lorsqu'un utilisateur souhaite afficher ou mettre à jour un graphique
     * en fonction de critères sélectionnés (espèce, type, zones, saison, etc.).
     * 
     * Étapes principales :
     * 1. Vérifie si un traitement est déjà en cours pour éviter les appels concurrents.
     * 2. Vérifie que les paramètres essentiels (id_espece et type) sont bien définis.
     * 3. S'assure qu'une seule zone (cynegetique, indicative ou secteur) est sélectionnée à la fois.
     * 4. Vérifie que les actions et fonctions de traitement associées au type sont bien définies.
     * 5. Lance la récupération des données via le store Vuex, puis traite les données reçues pour
     *    générer les options du graphique.
     * 6. Gère les erreurs en cas d'absence de données ou d'échec de la requête.
     * 
     * Cas d'utilisation :
     * - Utilisée lors de la génération ou de la mise à jour d'un graphique de chasse selon les filtres
     *   sélectionnés par l'utilisateur dans l'interface.
     * - Permet de s'assurer que les données affichées sont cohérentes avec les choix de l'utilisateur
     *   et que les erreurs sont correctement remontées à l'interface.
     */
    process() {
      if (this.processing) {
        return;
      }

      if (!(this.id_espece && this.type)) {
        return;
      }

      // test qu'il n'y ai pas 2 valeur pour zi zc secteur
      if (
        !!this.id_zone_cynegetique.length +
          !!this.id_zone_indicative.length +
          !!this.id_secteur.length >
        1
      ) {

        return;
      }

      if (!(this.actions[this.type] && this.processData[this.type])) {
        console.error(
          `Pas de fonctionalité définies pour le type ${this.type}`
        );
        return;
      }

      this.processing = true;

      this.$store
        .dispatch(this.actions[this.type], {
          id_espece: this.id_espece,
          id_zone_cynegetique: this.id_zone_cynegetique,
          id_zone_indicative: this.id_zone_indicative,
          id_secteur: this.id_secteur,
          id_saison: this.id_saison,
          bracelet: this.id_bracelet,
          poids_ou_dagues: this.poids_ou_dagues
        })
        .then(
          data => {
            this.chartOptions = this.processData[this.type](data, this.$props);
            this.processing = false;
          },
          error => {
            this.msgError = `pas de données pour les valeurs suivantes id_espece ${this.id_espece} id_zone_cynegetique ${this.id_zone_cynegetique} id_zone_indicative ${this.id_zone_indicative}`;
            this.bError = true;
            this.processing = false;
            this.chartOptions = null;
          }
        );

    }
  },
  mounted() {
    this.process();
  }
};
</script>
