<template>
  <div class="page-restitution">
    <div class="container">
      <div class="result" v-if="results">

        <div v-if="results.display == 'table'">
          <table-restitution :results="results"></table-restitution>
        </div>

        <div v-if="results.display == 'map'">
          <map-restitution :results="results"></map-restitution>
        </div>

        <div v-if="results.display == 'graph'">
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
import restitution from "./restitution.vue";
import tableRestitution from "./table-restitution";
import mapRestitution from "./map-restitution";
import "./restitution.css";
import configDeclaration from "./config-declarations.js";

export default {
  name: "test-restitution",
  components: {
    restitution,
    tableRestitution,
    mapRestitution,
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
