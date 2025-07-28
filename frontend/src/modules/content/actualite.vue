

<!--
  Composant Vue.js pour la gestion et l'affichage des actualités.

  - Affiche un bouton "Ajouter une actualité" uniquement si l'utilisateur possède un droit maximal supérieur ou égal à 5.
    Ce bouton permet de naviguer vers la page de création d'une nouvelle actualité.

  - Parcourt la liste des contenus (actualités) et affiche chaque élément à l'aide du composant personnalisé <oeasc-content>.
    Chaque contenu est identifié par son code unique, et la date de publication est affichée.

  - Utilise les composants Vuetify <v-btn> et <v-icon> pour le style et l'ergonomie du bouton d'ajout.

  - La propriété "displayContentDate" permet d'afficher la date de chaque actualité.
    La propriété "link" définit le type de lien associé au contenu.

  - La gestion des droits d'accès est réalisée via le getter "$store.getters.droitMax" provenant du store Vuex.
-->
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
import oeascContent from "./content.vue";
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
      const options = {
        ...configStore.options,
        "tags.nom_tag": this.tagNames
      }

      this.$store.dispatch(configStore.getAll, options).then(contents => {
        this.contents = contents.sort((c1, c2)  => c1.meta_create_date < c2.meta_create_date);
      });
    }
  },
  mounted() {
    this.getContents();
  }
};
</script>



<style></style>
