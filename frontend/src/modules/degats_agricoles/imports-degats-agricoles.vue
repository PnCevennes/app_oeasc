<template>
  <div>
    <br />
    <h1>Importation des dégâts agricoles</h1>
    <br />

    <div :disabled="uploading">
      <div style="max-width: 650px">
        <!-- input pour sélectionner le fichier à importer (la saison vient de la colonne « Campagnes comptables ») -->
        <v-file-input
          v-model="file"
          label="Sélectionner un fichier (csv, xls ou ods)"
          accept=".csv,.xls,.ods"
          outlined
          dense
          hide-details
        ></v-file-input>

        <!-- checkbox pour demander la confirmation de la mise à jour des données existantes (affiche_popup_update) avant l'import, qui affiche une popup de confirmation si cochée. Si la personne confirme dans la popup. -->
        <v-checkbox
          :input-value="doUpdate"
          @change="afficherPopup"
          v-model="doUpdate"
          label="Mettre à jour les données existantes"
          hide-details
        ></v-checkbox>
      </div>

      <div style="margin-top: 1rem; align-items: center; margin: auto">
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
            @click="clear"
            :disabled="uploading"
          >
            Annuler
          </v-btn>
        </div>
      </div>
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
      <div style="margin-top: 0.15rem; font-size: 0.8rem; color: #888">
        Le traitement s'exécute sur le serveur et se terminera même si l'opération est longue. Merci
        de patienter sans fermer cette page.
      </div>
    </div>

    <!-- affichage des messages de succès ou d'erreur après l'import -->
    <div
      v-if="message"
      class="mt-3"
    >
      <div
        v-if="error"
        style="color: crimson"
      >
        {{ message }}
      </div>
      <div
        v-else
        style="color: green"
      >
        {{ message }}
      </div>
    </div>

    <!-- affichage de json_data_bdd sous forme du tableau -->
    <div
      style="margin-top: 1rem; max-width: 100%"
      v-if="reponse_affichee.length > 0"
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
                v-else-if="value.type === 'info'"
                color="green"
                left
              >
                mdi-check-circle
              </v-icon>
              <v-icon
                v-else-if="value.type === 'warning'"
                color="orange"
                left
              >
                mdi-alert
              </v-icon>
              <span>{{ value.message }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- popup qui demande la confirmation pour la mise à jour des données existantes si l'utilisateur a coché la checkbox -->
    <v-dialog
      v-model="affiche_popup_update"
      max-width="500"
    >
      <v-card>
        <v-card-title class="headline">Confirmer la mise à jour</v-card-title>
        <v-card-text>
          Vous avez demandé une mise à jour des données existantes. Les déclarations des dossiers
          présents dans le fichier seront supprimées puis réimportées, et aucun retour en arrière ne
          sera possible. Confirmez-vous l'opération ?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="red"
            variant="text"
            @click="close_popup_update"
          >
            NON Annuler
          </v-btn>
          <v-btn
            color="green"
            variant="text"
            @click="confirmUpdate_action"
          >
            Confirmer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import {
  asyncImportMixin,
  updatePopupMixin,
  parseJournal,
} from '@/core/js/mixins/async-import.js';

export default {
  name: 'imports-degats-agricoles',
  mixins: [asyncImportMixin, updatePopupMixin],
  data() {
    return {
      file: null,
      uploading: false,
      message: '',
      reponse_affichee: [],
      error: false,
    };
  },
  methods: {
    clear() {
      // réinitialise tout si la personne clic sur annuler
      this.resetAsyncImport();
      this.file = null;
      this.message = '';
      this.error = false;
      this.doUpdate = false;
      this.affiche_popup_update = false;
      this.reponse_affichee = [];
      this.uploading = false;
    },

    async upload() {
      if (!this.file) {
        this.message = 'Aucun fichier sélectionné.';
        this.error = true;
        return;
      }

      this.message = '';
      this.error = false;
      this.reponse_affichee = [];
      this.uploading = true;

      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('update', this.doUpdate.toString());
      await this.startAsyncImport('api/agricole/import', formData);
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
        this.message = 'Importation terminée.';
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
</style>
