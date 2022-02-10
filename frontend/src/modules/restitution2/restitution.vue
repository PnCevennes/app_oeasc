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
import props from './config/props';

export default {
  name: "restitution2",
  components: {
    restitutionGraph,
  },
  props: [...props, 'display']
}

</script>