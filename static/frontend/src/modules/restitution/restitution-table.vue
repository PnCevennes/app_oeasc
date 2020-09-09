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
      <tbody
        v-for="(result, index) of [
          results.choix.choix1,
          results.choix.choix2
        ].filter(v => !!v)"
        :key="`${index}`"
      >
        <tr v-if="index">
          <td colspan="4"></td>
        </tr>

        <tr>
          <td class="title" colspan="4">{{ result.text }}</td>
        </tr>
        <template v-for="(result, index1) of result.dataList">
          <tr :key="`${index}_${index1}`">
            <td>{{ result.text }}</td>
            <td>{{ result.count }}</td>
            <td>
              <v-icon v-if="result.color" :style="`color: ${result.color}`"
                >stop_circle</v-icon
              >
              <span v-else>Non</span>
            </td>
            <td>
              <v-icon v-if="result.icon">mdi-{{ result.icon }}</v-icon>
              <span v-else>Non</span>
            </td>
          </tr>
          <tr
            style="opacity: 0.3"
            v-for="(result2, index2) of result.data2 || []"
            :key="`${index}_${index1}_${index2}`"
          >
            <td>- {{ result2.text }}</td>
            <td>{{ result2.count }}</td>
            <td>
              <v-icon v-if="result2.color" :style="`color: ${result2.color}`"
                >stop_circle</v-icon
              >
              <span v-else>Non</span>
            </td>
            <td>
              <v-icon v-if="result2.icon" style>mdi-{{ result2.icon }}</v-icon>
              <span v-else>Non</span>
            </td>
          </tr>
        </template>
      </tbody>
    </v-simple-table>
  </div>
</template>

<script>
export default {
  name: "restitution-table",
  props: ["results"]
};
</script>

<style scoped>
td.title {
  font-weight: bold;
}
</style>
