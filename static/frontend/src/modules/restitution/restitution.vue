<template>
  <div>
    <div v-if="results">
      <div v-if="display == 'table'">
        <restitution-table :results="results"></restitution-table>
      </div>

      <div v-if="display == 'map'">
        <restitution-map :results="results"></restitution-map>
      </div>

      <div v-if="display == 'graph'">
        <restitution-graph :results="results"></restitution-graph>
      </div>

      <div class="infos">
        Données {{results.nbDataFiltered}} / {{results.nbData}}.
        <template
          v-if="results.filtersDisplay"
        >Filtres : {{results.filtersDisplay}}</template>
      </div>
    </div>
    <div v-else>
      <p>Chargement des données en cours</p>
      <v-progress-linear active indeterminate></v-progress-linear>
    </div>

    <v-snackbar color="error" v-model="bError" :timeout="5000">{{ msgError }}</v-snackbar>
  </div>
</template>

<script>
import { Restitution } from "./restitution.js";
import restitutionTable from "./restitution-table";
import restitutionMap from "./restitution-map";
import restitutionGraph from "./restitution-graph";

const props = [
  "dataType",
  "display",
  "choix1",
  "choix2",
  "filters",
  "nbMax1",
  "nbMax2",
  "typeGraph",
  "stacking",
  "n",
  "height",
  "preFilters",
  "groupByKey",
];

export default {
  name: "restitution",
  props: props,
  components: {
    restitutionGraph,
    restitutionMap,
    restitutionTable,
  },
  data: () => ({
    results: null,
    bError: false,
    msgError: null,
    restitution: null,
  }),
  watch: {
    dataType() {
      this.initRestitution();
    },
  },
  methods: {
    initRestitution() {
      if (!this.dataType) {
        return;
      }

      this.restitution = new Restitution(this.dataType, this.$store);
      this.setRestitutionConfig();
      if (!this.restitution.getConfig(this.$store)) {
        this.bError = true;
        this.msgError = `Pas de configuration trouvée pour le type de donnée ${this.dataType}`;
        return;
      }
      /** recupération des données (dispatch) */
      this.restitution.getData(this.$store).then(
        () => {
          /** calcul de results */
          
          this.processData();
        },
        (error) => {
          this.bError = true;
          this.msgError = error;
        }
      );
    },
    setRestitutionConfig() {
      const options = {};
      for (const prop of props) {
        options[prop] = this[prop];
      }
      this.restitution.setOptions(options);
    },
    processData() {
      if (!this.restitution) {
        return;
      }
      this.setRestitutionConfig();

      const nbData = this.restitution.data().length;
      if (!(this.choix1 && this.display && nbData)) {
        return;
      }
      
      this.results = this.restitution.results();
    },
    baywatch: function (props, watcher) {
      var iterator = function (prop) {
        this.$watch(prop, watcher);
      };
      props.forEach(iterator, this);
    },
  },

  mounted() {
    console.log('mounted')
    this.baywatch(props, () => {
      this.processData();
    });
    this.initRestitution();
  },
};
</script>
<style scoped>
.infos {
  font-size: 0.8em;
  color: rgb(80, 80, 80);
}
</style>
