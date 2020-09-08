<template>
  <div v-if="results" class="restitution-table">
    <v-simple-table dense>
      <thead>
        <tr>
          <th>Texte</th>
          <th>Nombre</th>
          <th>Couleur</th>
          <th>Icône</th>
        </tr>
      </thead>
      <tbody v-for="(result, index1) of [results.choix.choix1, results.choix.choix2]" :key="index1">
        <tr v-if="index1">
          <td colspan="4"></td>
        </tr>
        
        <tr>
          <td class="title" colspan="4">{{result.text}}</td>
        </tr>
        <tr v-for="(result, index) of result.dataList" :key="index">
          <td>{{ result.text }}</td>
          <td>{{ result.count }}</td>
          <td>
            <v-icon v-if="result.color" :style="`color: ${result.color}`">stop_circle</v-icon>
            <span v-else>Non</span>
          </td>
          <td>
            <v-icon v-if="result.icon">mdi-{{ result.icon }}</v-icon>
            <span v-else>Non</span>
          </td>
        </tr>
      </tbody>
    </v-simple-table>
  </div>
</template>

<script>
export default {
  name: "restitution-table",
  props: ["results"],
};
</script>

<style scoped>
td.title {
  font-weight: bold;
}
</style>
