<!-- // Composant Vue.js pour l'export des données liées à la chasse.
// Affiche deux boutons permettant de télécharger les données sous différents formats (CSV et ODS).
// Utilisé dans le module "chasse" de l'application pour permettre aux utilisateurs d'exporter les réalisations de chasse.

// Méthode UrlExport :
//   - Génère une URL d'export pour un type de données et un format d'export donnés.
//   - Utilisée pour le bouton d'export CSV des réalisations de chasse.
//   - Paramètres :
//       - dataType (string) : le type de données à exporter (ex : 'realisation').
//       - exportType (string) : le format d'export souhaité (ex : 'csv').
//   - Retourne : une URL complète pour lancer l'export.

// Méthode UrlExportOds :
//   - Génère une URL d'export pour le format ODS (tableur).
//   - Utilisée pour le bouton d'export du bilan de la saison en cours au format ODS.
//   - Retourne : une URL complète pour lancer l'export ODS. -->
<template>
  <div>
    <h1>Exports des données Chasse</h1>

    <h2>Réalisations</h2>
    <v-row dense>
      <v-col>
        <v-btn :href="UrlExport('realisation', 'csv')">CSV</v-btn>
        : Export CSV des données chasses
      </v-col>
    </v-row>
    <v-row dense>
      <v-col>
        <v-btn :href="UrlExportOds()">ODS</v-btn>
        : Tableur 'Bilan' pour la saison en cours
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { url } from '@/core/js/data/api.js';

export default {
  name: 'exports-chasse',
  data: () => ({}),
  methods: {
    UrlExport(dataType, exportType) {
      return url(`api/chasse/export/${exportType}`, { data_type: dataType }).toString();
    },
    UrlExportOds() {
      return url(`api/chasse/export/ods`).toString();
    },
  },
};
</script>
