<template>
  <div>
    <h1>Exports des données Chasse</h1>

    <h2>Réalisations</h2>
    <v-row dense>
      <v-col>
        <v-btn :href="UrlExport('realisation', 'csv')">
          CSV
        </v-btn>
        : Export CSV des données chasses
      </v-col>
    </v-row>
        <v-row dense>
      <v-col>
        <v-btn :href="UrlExportOds('realisation', 'csv')">
          ODS
        </v-btn>
        : Tableur 'Bilan' pour la saison en cours
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
      return url(`api/chasse/export/${exportType}`, { data_type: dataType });
    },
    UrlExportOds() {
      return url(`api/chasse/export/ods`);
    }
  }
};
</script>
