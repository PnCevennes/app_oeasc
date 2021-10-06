<!--

Composant de restitution

utilisé dans le restitution-dashboard

selon les propriété affiche

 - un graph
 - un tableau TODO
 - une carte TODO

peut être utilisé dans les contenus

-->

<template>
  <div>
    <div v-if="display == 'graph'">
      <restitution-graph v-bind="$props"></restitution-graph>
    </div>
  </div>
</template>

<script>

import restitutionGraph from "./restitution-graph";

export default {
  name: "restitution2",
  components: {
    restitutionGraph,
  },
  props: [
    "dataType", // type de données (chasse) => quelle api / view est utilisée pour les données
    "fieldName", // quel champs est utilsé pour les rendus
    "fieldName2", // quel champs est utilsé pour les rendus (sous graphe)
    "height", // hauteur du composant
    "width", // largeur du composant
    "title", // titre du composant
    "typeGraph", // type de graphique : ['pie', 'bar', 'colmun']
    "filters", // filtres
    "display", // choix du type d'element de ['map', 'graph', 'table']
  ],
}

</script>