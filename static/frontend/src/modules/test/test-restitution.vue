<template>
  <div>
    <h1>Test restitution</h1>
    <div class="flex-container">
      <div>
        <h2>Résultats</h2>
        <div></div>
      </div>
      <div>
        <restitution :dataIn="declarations" :config="configDeclaration"> </restitution>
      </div>
    </div>
  </div>
</template>

<script>
import restitution from "./restitution.vue";
import "./restitution.css";
import configDeclaration from './config-declarations.js'

export default {
  name: "test-restitution",
  components: {
    restitution
  },
  data: () => ({
    declarations: null,
    configDeclaration
  }),
  mounted() {
    this.$store.dispatch("declarations").then(declarations => {
        this.declarations = declarations;
    });
  }
};
</script>
