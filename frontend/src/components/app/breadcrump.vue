<!-- 
/**
 * Composant Vue "breadcrump" (fil d'Ariane) :
 * 
 * Ce composant affiche le fil d'Ariane en haut de la page, permettant à l'utilisateur
 * de visualiser la hiérarchie de navigation courante à partir de la route active.
 * 
 * Template :
 * - Utilise le composant <v-breadcrumbs> de Vuetify pour afficher la liste des éléments du fil d'Ariane.
 * - Les éléments sont générés dynamiquement selon la route active.
 * 
 * Script :
 * - name: "breadcrump" : Nom du composant.
 * - computed:
 *   - getBreadcrumpList : Calcule la liste des éléments du fil d'Ariane à partir du nom de la route courante.
 *     Utilise la méthode breadcrumpList pour construire la liste récursivement.
 * - methods:
 *   - breadcrumpList(name, list) : Fonction récursive qui construit la liste du fil d'Ariane.
 *     - Recherche la route correspondante dans la configuration du routeur.
 *     - Ajoute un objet { text, to } à la liste, où "text" est le label de la route (ou le paramètre "code" si absent),
 *       et "to" est le chemin de la route.
 *     - Remonte récursivement vers la route parente jusqu'à la racine.
 * 
 * Style :
 * - .breadcrumbs : Ajoute un padding autour du fil d'Ariane pour l'intégration visuelle.
 */ -->

<template>
  <div class="breadcrumbs">
    <span>
      <v-breadcrumbs
        :items="getBreadcrumpList"
        class="pa-0"
      ></v-breadcrumbs>
    </span>
  </div>
</template>

<script>
export default {
  // Création d'un fil d'ariane
  name: 'breadcrump',
  computed: {
    getBreadcrumpList() {
      const name = this.$route.name;
      return this.breadcrumpList(name, []);
    },
  },
  methods: {
    breadcrumpList(name, list) {
      if (!name) {
        return list;
      }

      const route = this.$router.options.routes.find((route) => route.name == name);
      list.unshift({
        text: route.label || this.$route.params.code,
        to: route.path,
      });
      return this.breadcrumpList(route.parent, list);
    },
  },
};
</script>

<style>
.breadcrumbs {
  padding: 12px;
  padding-bottom: 0px !important;
}
</style>
