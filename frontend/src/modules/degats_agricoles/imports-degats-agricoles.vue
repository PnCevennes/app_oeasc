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
        v-if="etape_message"
        style="margin-top: 0.35rem; font-size: 0.9rem; color: #555"
      >
        {{ etape_message }}
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
import { simple_fetch } from '@/core/js/data/api.js';

export default {
  name: 'imports-degats-agricoles',
  data() {
    return {
      file: null,
      uploading: false,
      message: '',
      reponse_affichee: [],
      error: false,
      doUpdate: false,
      affiche_popup_update: false, // etat de la checkbox
      id_import: null, // id de la ligne de suivi de l'import lancé en tâche de fond
      etape_message: '', // libellé de l'étape en cours (ex. "Étape 3/5 : ...")
      pollTimer: null, // timer de polling du statut
    };
  },
  methods: {
    clear() {
      // réinitialise tout si la personne clic sur annuler
      this.stopPolling();
      this.file = null;
      this.message = '';
      this.error = false;
      this.doUpdate = false;
      this.affiche_popup_update = false;
      this.reponse_affichee = [];
      this.id_import = null;
      this.etape_message = '';
      this.uploading = false;
    },

    stopPolling() {
      if (this.pollTimer) {
        clearTimeout(this.pollTimer);
        this.pollTimer = null;
      }
    },

    close_popup_update() {
      // ferme la popup de confirmation pour la mise à jour des données existantes et décoche la checkbox
      this.doUpdate = false;
      this.affiche_popup_update = false;
    },

    afficherPopup() {
      // affiche la popup de confirmation pour la mise à jour des données existantes
      if (this.doUpdate == true) {
        this.affiche_popup_update = true;
      }
    },

    confirmUpdate_action() {
      // Si la personne confirme la mise à jour dans la popup, on passe doUpdate à true
      this.affiche_popup_update = false;
      this.doUpdate = true;
    },

    async upload() {
      if (!this.file) {
        this.message = 'Aucun fichier sélectionné.';
        this.error = true;
        return;
      }

      this.stopPolling();
      this.message = '';
      this.error = false;
      this.reponse_affichee = [];
      this.etape_message = '';
      this.id_import = null;

      try {
        this.uploading = true;
        const formData = new FormData();
        formData.append('file', this.file);
        formData.append('update', this.doUpdate.toString());

        // Lancement de l'import : le backend enregistre le fichier, crée une ligne
        // de suivi et traite en tâche de fond. Réponse immédiate (202) avec id_import.
        const response = await simple_fetch('POST', 'api/agricole/import', formData);

        // simple_fetch redirige vers /login et retourne undefined en cas de 401
        if (!response) {
          this.message = 'Vous devez être connecté pour importer un fichier.';
          this.error = true;
          this.uploading = false;
          return;
        }

        if (response.success === false || !response.id_import) {
          this.message = response.user_message || "Erreur lors du lancement de l'import.";
          this.error = true;
          this.uploading = false;
          return;
        }

        this.id_import = response.id_import;
        this.etape_message = 'Import en attente de traitement…';
        this.pollStatus();
      } catch (err) {
        console.error("Erreur lors de l'import:", err);
        this.message = err.message || "Erreur lors de l'import.";
        this.error = true;
        this.uploading = false;
      }
    },

    async pollStatus() {
      // interroge périodiquement l'état de l'import jusqu'à TERMINE / ERREUR
      if (!this.id_import) return;
      let res;
      try {
        res = await simple_fetch('GET', `api/agricole/import/status/${this.id_import}`);
      } catch (err) {
        console.error('pollStatus:', err);
        // on retente quelques instants plus tard plutôt que d'abandonner
        // abandon après 20 échecs consécutifs (~1 min) au lieu de boucler indéfiniment
        this.pollFailures = (this.pollFailures || 0) + 1;
        if (this.pollFailures >= 20) {
          this.pollFailures = 0;
          this.stopPolling();
          this.message = 'Suivi de l’import interrompu : serveur injoignable.';
          this.error = true;
          this.uploading = false;
          return;
        }
        this.pollTimer = setTimeout(() => this.pollStatus(), 3000);
        return;
      }

      this.pollFailures = 0;
      if (!res || res.success === false || !res.import_status) {
        this.message = (res && res.user_message) || "Suivi de l'import indisponible.";
        this.error = true;
        this.uploading = false;
        return;
      }

      const st = res.import_status;
      this.traitement_journal(st.journal || []);
      this.etape_message = st.message || '';

      if (st.statut === 'TERMINE' || st.statut === 'ERREUR') {
        this.stopPolling();
        this.uploading = false;
        this.etape_message = '';
        if (st.statut === 'ERREUR' || st.success === false) {
          this.error = true;
          if (st.message) this.message = st.message;
        } else {
          this.message = 'Importation terminée.';
        }
        return;
      }

      // toujours en cours : on reprogramme un poll
      this.pollTimer = setTimeout(() => this.pollStatus(), 2000);
    },

    traitement_journal(journal) {
      // reconstruit reponse_affichee à partir du journal (liste de lignes taguées
      // [ERROR] / [INFO] / [WARNING]). Idempotent : appelé à chaque poll.
      const lines = Array.isArray(journal) ? journal : [];
      const maxDisplay = 1000;
      const out = [];

      for (const log of lines) {
        if (log.includes('[ERROR]')) {
          out.push({ type: 'error', message: log.replace('[ERROR] ', '') });
        } else if (log.includes('[INFO]')) {
          out.push({ type: 'info', message: log.replace('[INFO] ', '') });
        } else if (log.includes('[WARNING]')) {
          out.push({ type: 'warning', message: log.replace('[WARNING] ', '') });
        }
      }

      this.reponse_affichee = out.length > maxDisplay ? out.slice(-maxDisplay) : out;
      return this.reponse_affichee;
    },
  },

  beforeUnmount() {
    // stoppe le polling si l'utilisateur quitte la page pendant un import
    this.stopPolling();
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
