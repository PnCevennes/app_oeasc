<template>
  <div class="page-restitution">
    <div class="container-restitution">
      <div class="result" v-if="results">
        <div v-if="results.display == 'table'">
          <table-restitution :results="results"></table-restitution>
        </div>

        <div v-if="results.display == 'map'">
          <map-restitution :results="results">
          </map-restitution>
        </div>

        <div v-if="results.display == 'graph'">
          <graph-restitution :results="results"></graph-restitution>
        </div>
      </div>
      <div class="restitution">
        <restitution
          :dataIn="declarations"
          :config="configDeclaration"
          @updateResults="results = $event"
        >
        </restitution>
      </div>
    </div>
  </div>
</template>

<script>
import restitution from "./config-restitution.vue";
import tableRestitution from "./table-restitution";
import mapRestitution from "./map-restitution";
import graphRestitution from "./graph-restitution";
import "./restitution.css";
import configDeclaration  from "./config/declarations.js";

export default {
  name: "test-restitution",
  components: {
    restitution,
    tableRestitution,
    mapRestitution,
    graphRestitution,
  },
  data: () => ({
    declarations: null,
    configDeclaration,
    results: null,
  }),
  mounted() {
    this.$store.dispatch("declarations").then(declarations => {
      this.declarations = declarations;
    });
  }
};
</script>
