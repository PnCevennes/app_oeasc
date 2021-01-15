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

      <!-- <div class="infos">
        Données {{results.nbDataFiltered}} / {{results.nbData}}.
        <template
          v-if="results.filtersDisplay"
        >Filtres : {{results.filtersDisplay}}</template>
      </div> -->
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
import deepEqual from "fast-deep-equal";

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
          setTimeout(() =>{             
          this.processData();
          }, 100)
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
      if (!(this.restitution && this.restitution._options.choix1)) {
        return;
      }
      this.setRestitutionConfig();


      const nbData = this.restitution.data().length;
      if (!(this.choix1 && this.display && nbData)) {
      
        return;
      }
      const results = {...this.restitution.results()};
      const options = {}
      for(const key of props) {
        options[key] = this[key] || results.options[key];
      }
      results.options = options;
      this.results = results
    },
    baywatch: function (props, watcher) {
      var iterator = function (prop) {
        this.$watch(prop, watcher(prop));
      };
      props.forEach(iterator, this);
    },
  },

  mounted() {
    this.baywatch(props, (prop) => (value) => {
      if(Object.keys(value).length) {
        if(!deepEqual(value, this.results.options[prop])) {
          console.log(prop, value, this.results.options.filters)
          this.processData();
        }
      }
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
