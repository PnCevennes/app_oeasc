<template>
  <div>
    <div v-if="declaration">
      <h1>Déclaration {{ declaration.id_declaration }}</h1>
      <div>
        <declaration-table :declaration="declaration"></declaration-table>
      </div>
      <div>Cartes</div>
    </div>
  </div>
</template>

<script>
import declarationTable from "./declaration-table";

export default {
  name: "declaration",
  data: () => ({
    idDeclaration: null,
    declaration: null
  }),
  components: { declarationTable },
  methods: {
    initDeclaration() {
      this.idDeclaration = this.$route.params.idDeclaration;
      this.declaration = this.$store
        .dispatch("declarations")
        .then(declarations => {
          this.declaration = declarations.find(
            d => this.idDeclaration == d.id_declaration
          );
        });
    }
  },
  created: function() {
    this.initDeclaration();
  },
  watch: {
    $route() {
        this.initDeclaration();
    }
  }
};
</script>
