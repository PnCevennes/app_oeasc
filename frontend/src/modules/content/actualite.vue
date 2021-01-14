<template>
  <div>
    <div v-if="$store.getters.droitMax>=5">
      <v-btn 
        color="success"
        to="/actualite/"
      >
        <v-icon>
          fa-plus
        </v-icon>
        Ajouter une actualité
      </v-btn>
    </div>

    <div v-for="content of contents" :key="content.code"  class="page">
      <oeasc-content
        :key="content.code"
        displayContentDate="true"
        :code="content.code"
        link="actualite"
      ></oeasc-content>
    </div>
  </div>
</template>
<script>
import oeascContent from "./content";
export default {
  name: "actualites",
  props: ["tagNames"],
  components: { oeascContent },
  data: () => ({
    contents: null
  }),
  methods: {
    getContents() {
      const storeName = "commonsContent";
      const configStore = this.$store.getters.configStore(storeName);
      this.$store.dispatch(configStore.getAll).then(contents => {
        this.contents = contents
        .filter(content =>
          this.tagNames && this.tagNames.length
            ? this.tagNames.every(nom_tag => {
                return content.tags.map(t => t.nom_tag).includes(nom_tag);
              })
            : true
        ).sort((c1, c2)  => c1.meta_create_date < c2.meta_create_date);
      });
    }
  },
  mounted() {
    this.getContents();
  }
};
</script>
<style></style>
