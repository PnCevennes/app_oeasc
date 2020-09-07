<template>
  <div>    
    <div v-if="results">
      <div v-if="display == 'table'">
        <table-restitution :results="results"></table-restitution>
      </div>

      <div v-if="display == 'map'">
        <map-restitution :results="results"> </map-restitution>
      </div>

      <div v-if="display == 'graph'">
        <graph-restitution :results="results"></graph-restitution>
      </div>
    </div>
    <div v-else>
      <p>Chargement des données en cours</p>
        <v-progress-linear active indeterminate></v-progress-linear>
</div>

    <v-snackbar color="error" v-model="bError" :timeout="5000">
      {{ msgError }}
    </v-snackbar>
  </div>
</template>

<script>
import { restitution } from "./restitution-utils.js";
import tableRestitution from "./table-restitution";
import mapRestitution from "./map-restitution";
import graphRestitution from "./graph-restitution";

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
  "height"
];

export default {
  name: "restitution",
  props: props,
  components: {
    mapRestitution,
    graphRestitution,
    tableRestitution
  },
  data: () => ({
    dataRestitution: null,
    results: null,
    bError: false,
    msgError: null,
    configRestitution: null
  }),
  watch: {
    dataType() {
      this.initRestitution();
    }
  },
  methods: {
    
    initRestitution() {
      if (!this.dataType) {
        return;
      }
      this.configRestitution = this.$store.getters.configRestitution(
        this.dataType
      );
      if (!this.configRestitution) {
        this.bError = true;
        this.msgError = `Pas de configuration trouvée pour le type de donnée ${this.dataType}`;
        return;
      }
      console.log("initRestitution", this.dataType, this.configRestitution);

      /** recupération des données (dispatch) */
      this.$store.dispatch(this.configRestitution.getData).then(
        data => {
          this.dataRestitution = data;
          /** calcul de result */
          this.processData();
        },
        error => {
          this.bError = true;
          this.msgError = error;
        }
      );
    },
    processData() {
      const nbData = this.dataRestitution ? this.dataRestitution.length : 0;
      console.log(`calcul du résultat avec ${nbData} données`);
      if (!(this.choix1 && this.display && nbData)) {
        return;
      }

      const options = {};
      for (const prop of props) {
        options[prop] = this[prop];
      }

      this.results = restitution.results(this.dataRestitution, {
        ...this.configRestitution,
        ...options
      });
    },
    baywatch: function(props, watcher) {
      var iterator = function(prop) {
        this.$watch(prop, watcher);
      };
      props.forEach(iterator, this);
    }
  },

  mounted() {
    this.baywatch(props, () => {
      this.processData();
    });
    this.initRestitution();
  }
};
</script>
