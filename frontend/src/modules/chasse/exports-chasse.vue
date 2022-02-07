<template>
<div>
  <h1> Exports des données Chasse</h1>

<h2>Réalisations</h2>
            <v-row dense>

<v-col>
  <v-btn
    :href="UrlExport('realisation', 'csv')"
  >
    CSV
  </v-btn>
  </v-col>
            </v-row>
</div>
</template>

<script>
import { url } from "@/core/js/data/api.js";

export default {
  name: "exports-chasse",
  data: () => ({}),
  methods: {
    UrlExport(dataType, exportType) {
      return url(`api/chasse/export/${exportType}`, { data_type: dataType })
    }
    // downloadExport(dataType, exportType) {
    //   console.log(`Export ${dataType} ${exportType}`)
    //   this.$store.dispatch('exportChasse', { dataType, exportType }).then(
    //     () => {
    //       console.log(`L'Export ${dataType} de type ${exportType} à bien été réalisé`)
    //     }
    //   )
    // }
  }
}
</script>
