<template>
  <div v-if="results" class="restitution-table">
    <div v-for="(result, index) of [results.choix.choix1, results.choix.choix2]" :key="index">
      <div v-if="result">
        <h3>{{ result.text }}</h3>

        <v-simple-table dense>
          <thead>
            <tr>
              <th>Texte</th>
              <th>Nombre</th>
              <th>Couleur</th>
              <th>Icône</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(result, index) of result.dataList" :key="index">
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
          </tbody>
        </v-simple-table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "table-restitution",
  props: ["results"]
};
</script>
