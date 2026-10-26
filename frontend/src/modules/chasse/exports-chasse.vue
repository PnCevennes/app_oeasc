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
  <v-container style="max-width: 1000px">
    <h1 class="mb-6">Exports des données Chasse</h1>

    <v-row>
      <v-col cols="12" md="7">
        <v-card variant="outlined" class="h-100" :class="{ 'export-loading': loading }">
          <v-card-title>Réalisations (CSV)</v-card-title>
          <v-card-subtitle class="text-wrap">
            Données de chasse sur une période de saisons
          </v-card-subtitle>
          <v-card-text>
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="saisonDebut"
                  :items="saisons"
                  item-title="nom_saison"
                  item-value="id_saison"
                  label="Saison de début"
                  density="compact"
                  variant="outlined"
                  hide-details="auto"
                  :disabled="loading"
                ></v-select>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="saisonFin"
                  :items="saisons"
                  item-title="nom_saison"
                  item-value="id_saison"
                  label="Saison de fin"
                  density="compact"
                  variant="outlined"
                  hide-details="auto"
                  :disabled="loading"
                ></v-select>
              </v-col>
            </v-row>
            <v-alert
              v-if="saisonDebut && saisonFin && !csvValide"
              type="error"
              density="compact"
              variant="tonal"
              class="mt-3"
            >
              La saison de début doit précéder la saison de fin.
            </v-alert>
          </v-card-text>
          <v-card-actions class="px-4 pb-4">
            <v-btn
              :loading="loadingCsv"
              :disabled="!csvValide || loading"
              @click="telecharger(urlExportCsv, 'csv')"
              color="primary"
              variant="flat"
              prepend-icon="mdi-download"
            >
              Télécharger CSV
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card variant="outlined" class="h-100" :class="{ 'export-loading': loading }">
          <v-card-title>Bilan (ODS)</v-card-title>
          <v-card-subtitle class="text-wrap">Tableur « Bilan » d'une saison</v-card-subtitle>
          <v-card-text>
            <v-select
              v-model="saisonOds"
              :items="saisons"
              item-title="nom_saison"
              item-value="id_saison"
              label="Saison à exporter"
              density="compact"
              variant="outlined"
              hide-details="auto"
                  :disabled="loading"
            ></v-select>
          </v-card-text>
          <v-card-actions class="px-4 pb-4">
            <v-btn
              :loading="loadingOds"
              :disabled="!saisonOds || loading"
              @click="telecharger(urlExportOds, 'ods')"
              color="primary"
              variant="flat"
              prepend-icon="mdi-download"
            >
              Télécharger ODS
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    <v-alert v-if="erreur" type="error" variant="tonal" class="mt-4" closable @click:close="erreur = null">
      {{ erreur }}
    </v-alert>

    <v-overlay :model-value="loading" persistent class="align-center justify-center">
      <div class="text-center">
        <v-progress-circular indeterminate size="64" color="primary"></v-progress-circular>
        <div class="mt-3">Création de l'export en cours…</div>
      </div>
    </v-overlay>
  </v-container>
</template>

<script>
import { url, apiRequest } from '@/core/js/data/api.js';

export default {
  name: 'exports-chasse',
  data: () => ({
    saisons: [],
    saisonDebut: null,
    saisonFin: null,
    saisonOds: null,
    loadingCsv: false,
    loadingOds: false,
    erreur: null,
  }),
  computed: {
    loading() {
      return this.loadingCsv || this.loadingOds;
    },
    csvValide() {
      const nom = (id) => (this.saisons.find((s) => s.id_saison === id) || {}).nom_saison;
      return !!this.saisonDebut && !!this.saisonFin && nom(this.saisonDebut) <= nom(this.saisonFin);
    },
    urlExportCsv() {
      if (!this.csvValide) return undefined;
      return url('api/chasse/export/csv', {
        data_type: 'realisation',
        id_saison_debut: this.saisonDebut,
        id_saison_fin: this.saisonFin,
      }).toString();
    },
    urlExportOds() {
      const saison = this.saisons.find((s) => s.id_saison === this.saisonOds);
      if (!saison) return undefined;
      return url('api/chasse/export/ods', { saison: saison.nom_saison }).toString();
    },
  },
  methods: {
    // Génère l'export côté serveur (peut être long) puis déclenche le téléchargement
    async telecharger(urlExport, format) {
      if (!urlExport || this.loading) return;
      const flag = format === 'csv' ? 'loadingCsv' : 'loadingOds';
      this[flag] = true;
      this.erreur = null;
      try {
        const response = await fetch(urlExport, { credentials: 'include' });
        if (!response.ok) throw new Error(`Erreur ${response.status}`);
        const blob = await response.blob();
        const disposition = response.headers.get('Content-Disposition') || '';
        const match = disposition.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = match ? decodeURIComponent(match[1]) : `export_chasse.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(a.href);
      } catch (e) {
        this.erreur = `Échec de l'export : ${e.message}`;
      } finally {
        this[flag] = false;
      }
    },
  },
  mounted() {
    apiRequest('GET', 'api/generic/chasse/saisons').then((res) => {
      // du plus récent au plus ancien
      this.saisons = (res.items || []).sort((a, b) => b.nom_saison.localeCompare(a.nom_saison));
      if (!this.saisons.length) return;
      const cur = this.saisons.find((s) => s.current) || this.saisons[0];
      // début par défaut : saison 2010 (sinon la plus ancienne)
      const debut =
        this.saisons.find((s) => String(s.nom_saison).startsWith('2010')) ||
        this.saisons[this.saisons.length - 1];
      this.saisonDebut = debut.id_saison;
      this.saisonFin = cur.id_saison;
      this.saisonOds = cur.id_saison;
    });
  },
};
</script>

<style scoped>
.export-loading {
  opacity: 0.5;
  pointer-events: none;
}
</style>
