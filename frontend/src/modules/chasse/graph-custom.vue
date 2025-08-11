<!--
  Ce composant Vue.js affiche un graphique personnalisé à l'aide de la bibliothèque Highcharts.
  - Le conteneur principal a une hauteur dynamique basée sur la prop `height` (par défaut 400px) et une largeur de 100%.
  - Si la donnée `processing` est fausse et que `chartOptions` est définie, le composant Highcharts est affiché avec les options et l'instance fournies.
    - Les props `width` et `height` permettent de personnaliser la taille du graphique.
    - `chartOptions` doit contenir la configuration du graphique Highcharts.
    - `hcInstance` doit être l'instance Highcharts à utiliser.
  - Si `processing` est vrai ou que `chartOptions` n'est pas encore disponible, une barre de progression linéaire (chargement) est affichée à la place du graphique.
  - Ce composant est utile pour afficher dynamiquement des graphiques avec gestion de l'état de chargement, par exemple lors de la récupération de données asynchrones.
-->
<template>
  <div :style="`height:${height || '400px'}; width: 100%`">
    <highcharts
      v-if="!processing && chartOptions"
      :style="`width:${width || '100%'}; height:${height || '400px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
    <v-progress-linear v-else active indeterminate></v-progress-linear>
  </div>
</template>

<script>
import Highcharts from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import processData from "./config/graph-custom.js";
import restitutionChasse from "./config/restitution-chasse.js";


// Initialise les modules d'exportation de Highcharts pour permettre l'export des graphiques
// exportingInit active les fonctionnalités d'export standard (PNG, PDF, etc.)
// offlineExporting permet l'export sans connexion à Internet
exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "graph-custom",
  props: ["field_name", "height", "width", "title", "typeGraph", "view"],
  // Déclaration des données réactives du composant
  data: () => ({
    // chartOptions : objet de configuration du graphique Highcharts, mis à jour après récupération et traitement des données
    chartOptions: null,
    // hcInstance : instance de la librairie Highcharts utilisée par le composant <highcharts>
    hcInstance: Highcharts,
    // processData : fonction utilitaire pour transformer les données brutes en options Highcharts (importée)
    processData: processData,
    // action : nom de l'action Vuex à dispatcher pour récupérer les données du graphique
    action: "chasseCustom",
    // processing : booléen indiquant si le composant est en cours de chargement (affiche la barre de progression si true)
    processing: false
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
     * Traite les données pour générer les options du graphique.
     * 
     * Cette fonction est appelée lorsqu'une action utilisateur nécessite la mise à jour du graphique,
     * par exemple lors d'un changement de filtre ou de champ sélectionné.
     * 
     * - Si un traitement est déjà en cours (`this.processing`), la fonction retourne immédiatement pour éviter les appels concurrents.
     * - Si `field_name` n'est pas défini, la fonction retourne également car il manque une information essentielle pour le traitement.
     * - Déclenche une action Vuex (`this.action`) en passant les propriétés du composant (`this.$props`) pour récupérer les données nécessaires.
     * - Une fois les données reçues, elles sont traitées par `processData` pour générer les options du graphique (`chartOptions`).
     * - Le flag `processing` est remis à `false` à la fin du traitement pour permettre de nouveaux appels.
     */
    process() {
      if (this.processing) {
          return
      }
      if (
        !(this.field_name)
      ) {
        return;
      }

      this.processing = true;
      this.$store
        .dispatch(this.action, this.$props)
        .then(data => {
          this.chartOptions = this.processData(data, this.$props, restitutionChasse);
          this.processing = false;
        });
    }
  },
  mounted() {
    this.process();
  }
};
</script>
