<template>
  <div>
    <h2>Importation des cultures et types de culture</h2>
    <p style="font-size: 0.9rem; color: #555; max-width: 850px">
      Permet de créer de nouvelles cultures et de les rattacher à un type de culture (les types
      absents sont créés). Les cultures déjà en base ne sont pas modifiées, sauf si la case
      « Mettre à jour » est cochée : leur type de culture est alors remplacé par celui du fichier.
    </p>

    <div style="max-width: 650px">
      <v-file-input
        v-model="file"
        label="Sélectionner un fichier (csv, xls, xlsx ou ods)"
        accept=".csv,.xls,.xlsx,.ods"
        variant="outlined"
        density="compact"
        :disabled="uploading"
        hide-details
      ></v-file-input>

      <v-checkbox
        v-model="doUpdate"
        label="Mettre à jour le type des cultures existantes"
        :disabled="uploading"
        hide-details
      ></v-checkbox>
    </div>

    <div
      class="mt-2"
      style="display: flex; gap: 12px"
    >
      <v-btn
        :disabled="!file || uploading"
        color="primary"
        @click="upload"
      >
        <v-icon left>mdi-upload</v-icon>
        Importer
      </v-btn>
      <v-btn
        variant="text"
        :disabled="uploading"
        @click="clear"
      >
        Annuler
      </v-btn>
    </div>

    <div
      v-if="uploading"
      class="mt-3"
    >
      <v-progress-linear
        indeterminate
        color="primary"
      ></v-progress-linear>
      <div
        v-if="etapeMessage"
        style="margin-top: 0.35rem; font-size: 0.9rem; color: #555"
      >
        {{ etapeMessage }}
      </div>
    </div>

    <div
      v-if="message"
      class="mt-3 journal"
      :style="{ color: error ? 'crimson' : 'green' }"
    >
      {{ message }}
    </div>

    <div
      v-if="reponse_affichee.length > 0"
      class="mt-3 journal"
    >
      <table>
        <thead>
          <tr>
            <th>JOURNAL</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(value, idx) in reponse_affichee"
            :key="idx"
          >
            <td>
              <v-icon
                v-if="value.type === 'error'"
                color="error"
                left
              >
                mdi-close-circle
              </v-icon>
              <v-icon
                v-else-if="value.type === 'warning'"
                color="orange"
                left
              >
                mdi-alert
              </v-icon>
              <v-icon
                v-else
                color="green"
                left
              >
                mdi-check-circle
              </v-icon>
              <span>{{ value.message }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      class="mt-4"
      style="max-width: 1000px; width: 100%"
    >
      <div style="font-size: 0.9rem; color: #555; margin-bottom: 0.25rem">
        Exemple de fichier attendu (une ligne par culture, deux colonnes) :
      </div>
      <div style="overflow-x: auto; max-width: 100%">
        <table class="exemple">
          <thead>
            <tr>
              <th
                v-for="c in exemple.colonnes"
                :key="c"
              >
                {{ c }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(ligne, i) in exemple.lignes"
              :key="i"
            >
              <td
                v-for="(v, j) in ligne"
                :key="j"
              >
                {{ v }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { asyncImportMixin, parseJournal } from '@/core/js/mixins/async-import.js';

export default {
  name: 'ImportCulturesDegatsAgricoles',
  mixins: [asyncImportMixin],
  data() {
    return {
      file: null,
      doUpdate: false,
      uploading: false,
      message: '',
      error: false,
      reponse_affichee: [],
      exemple: {
        colonnes: ['culture', 'type de culture'],
        lignes: [
          ['ABRICOTIERS', 'FRUITS ET LEGUMES'],
          ['BLE TENDRE', 'CEREALES'],
          ['PRAIRIE TEMPORAIRE', 'PRAIRIES ET FOURRAGES'],
        ],
      },
    };
  },
  methods: {
    clear() {
      this.resetAsyncImport();
      this.file = null;
      this.doUpdate = false;
      this.message = '';
      this.error = false;
      this.reponse_affichee = [];
      this.uploading = false;
    },

    async upload() {
      if (!this.file) return;
      this.message = '';
      this.error = false;
      this.reponse_affichee = [];
      this.uploading = true;
      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('update', String(this.doUpdate));
      await this.startAsyncImport('api/agricole/import_cultures', formData);
    },

    // --- hooks de asyncImportMixin
    statusUrl(idImport) {
      return `api/agricole/import/status/${idImport}`;
    },
    onImportProgress(st) {
      this.reponse_affichee = parseJournal(st.journal).lignes;
    },
    onImportFinished(st, hasError) {
      this.uploading = false;
      if (hasError) {
        this.error = true;
        if (st.message) this.message = st.message;
      } else {
        this.message = st.message || 'Importation terminée.';
      }
    },
    onImportError(message) {
      this.message = message;
      this.error = true;
      this.uploading = false;
    },
  },
};
</script>

<style scoped>
.mt-2 {
  margin-top: 0.5rem;
}
.mt-3 {
  margin-top: 1rem;
}
.mt-4 {
  margin-top: 1.5rem;
}
.journal {
  max-width: 1000px;
  width: 100%;
}
.journal table {
  width: 100%;
  table-layout: fixed;
}
.journal td,
.journal th {
  overflow-wrap: anywhere;
  word-break: break-word;
  text-align: left;
}
table.exemple {
  border-collapse: collapse;
  font-size: 0.8rem;
}
table.exemple th,
table.exemple td {
  border: 1px solid #ddd;
  padding: 0.25rem 0.5rem;
  white-space: nowrap;
}
table.exemple th {
  background: #f0f0f0;
}
</style>
