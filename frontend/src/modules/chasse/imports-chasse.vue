<template>
  <div>
    <br />
    <h1 style="text-align: center">Importation des données Chasse</h1>
    <br />

    <div :disabled="uploading">
      <div style="max-width: 650px; margin: 0 auto">
        <!-- formulaire select pour la saison, affiche la saison en cours par défaut -->
        <v-select
          v-model="saison"
          :items="saisons"
          item-title="nom_saison"
          item-value="id_saison"
          label="Saison"
          dense
          outlined
          clearable
        ></v-select>

        <!-- input pour sélectionner le fichier CSV à importer -->
        <v-file-input
          v-model="file"
          label="Sélectionner un fichier CSV"
          accept=".csv"
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
          style="display: flex; gap: 12px; justify-content: center"
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


    <!-- exemple de modèle de fichier à importer (noms de colonnes de l'export geochasse) -->
    <div class="modele-fichier">
      <h3>Exemple de fichier à importer</h3>
      <p class="modele-aide">
        Fichier CSV exporté depuis Geochasse (séparateur « ; » ou « , », encodage UTF-8), avec une
        ligne d'en-tête. Seules les colonnes ci-dessous sont utilisées, les autres colonnes de
        l'export sont ignorées. Le numéro de bracelet doit exister dans les attributions de la
        saison.
      </p>
      <div class="modele-scroll">
        <table class="modele-table">
          <thead>
            <tr>
              <th
                v-for="col in modeleColonnes"
                :key="col"
              >
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(ligne, idx) in modeleLignes"
              :key="idx"
            >
              <td
                v-for="(valeur, i) in ligne"
                :key="i"
              >
                {{ valeur }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="modele-aide">
        <b>ESPECE</b> : CERF, CHEVREUIL ou MOUFLON. <b>SEXE</b> : Male, Femelle ou Indéterminé.
        <b>PESEE</b> : Plein ou Vidé. <b>TYPE CHASSE</b> : Individuel, Collective ou Battue.
        <b>DATE</b> : jj/mm/aaaa ou aaaa-mm-jj. <b>LON</b> / <b>LAT</b> : degrés décimaux (WGS84).
      </p>
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
                v-else-if="value.type === 'file'"
                color="blue"
                left
              >
                mdi-file
              </v-icon>
              <v-icon
                v-else-if="value.type === 'warning'"
                color="orange"
                left
              >
                mdi-alert
              </v-icon>
              <span v-if="value.type === 'file'">
                Un fichier à été généré:
                <a
                  :href="create_url_fichier_erreur(value.message)"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ value.message }}
                </a>
              </span>
              <span v-else>{{ value.message }}</span>
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
          Vous avez demandé une mise à jour des données existantes. Les données seront écrasées et
          aucun retour en arrière ne sera possible. Confirmez-vous l'opération ?
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
import { apiRequest, url } from '@/core/js/data/api.js';
import {
  asyncImportMixin,
  updatePopupMixin,
  parseJournal,
} from '@/core/js/mixins/async-import.js';

export default {
  name: 'imports-chasse',
  mixins: [asyncImportMixin, updatePopupMixin],
  data() {
    return {
      file: null,
      uploading: false,
      message: '',
      reponse_affichee: [],
      error: false,
      saisons: [],
      saison: null,
      nom_fichier_erreur: null, // si il est différent de null, on propose un bouton de téléchargement du fichier d'erreur généré par le backend
      url_fichier_erreur: null,
      // noms de colonnes tels qu'ils sont exportés par Geochasse
      modeleColonnes: [
        'ID',
        'NUMERO',
        'ESPECE',
        'AGE',
        'SEXE',
        'POIDS',
        'PESEE',
        'TYPE CHASSE',
        'DATE',
        'COMMUNE',
        'LON',
        'LAT',
        'COMMENTAIRE',
        'NB CORS',
        'PARC_NOM_TIREUR',
        'PARC_LIEU_DIT',
      ],
      modeleLignes: [
        [
          '49816',
          'CEM006575',
          'CERF',
          'Adulte',
          'Male',
          '146.3',
          'Plein',
          'Battue',
          '2026-10-24',
          'FRAISSINET DE FOURQUES',
          '3.5412',
          '44.2105',
          '',
          '6',
          'Dupont Jean',
          'Tabilloux',
        ],
        [
          '49820',
          'CHF004512',
          'CHEVREUIL',
          'Jeune',
          'Femelle',
          '14.2',
          'Vidé',
          'Individuel',
          '2026-10-25',
          'LE PONT DE MONTVERT',
          '3.7935',
          '44.4153',
          '',
          '',
          'Martin Paul',
          'Fretma',
        ],
      ],
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
      this.nom_fichier_erreur = null;
      this.url_fichier_erreur = null;
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
      this.nom_fichier_erreur = null;
      this.url_fichier_erreur = null;
      this.uploading = true;

      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('update', this.doUpdate.toString());
      if (this.saison) {
        formData.append('saison', this.saison);
      }
      await this.startAsyncImport('api/chasse/import/traitement-csv', formData);
    },

    // --- hooks de asyncImportMixin
    statusUrl(idImport) {
      return `api/chasse/import/status/${idImport}`;
    },

    onImportProgress(st) {
      this.traitement_journal(st.journal || []);
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

    traitement_journal(journal) {
      const { lignes, fichierErreur } = parseJournal(journal);
      this.reponse_affichee = lignes;
      this.nom_fichier_erreur = fichierErreur;
      return this.reponse_affichee;
    },

    create_url_fichier_erreur(nom_fichier) {
      if (!nom_fichier) {
        console.error("Aucun fichier d'erreur disponible pour le téléchargement.");
        this.message = "Aucun fichier d'erreur disponible pour le téléchargement.";
        this.error = true;
        return null;
      }
      try {
        // Ne pas muter de propriété réactive depuis une fonction appelée en rendu
        // (évite boucle de rendu infinie). Retourner simplement l'URL.
        return url(`api/chasse/import/download-erreurs-csv/${nom_fichier}`).toString();
      } catch (e) {
        console.error('Erreur création URL fichier erreur:', e);
        this.message = "Erreur lors de la création du lien de téléchargement du fichier d'erreur.";
        this.error = true;
        return null;
      }
    },
  },

  mounted() {
    // récupérer les saisons disponibles via l'API
    apiRequest('GET', 'api/generic/chasse/saisons')
      .then((res) => {
        this.saisons = res.items || [];
        // tri des saisons par ordre décroissant d'id (du plus récent au plus ancien)
        this.saisons.sort((a, b) => b.id_saison - a.id_saison);
        // si aucune saison sélectionnée, définir la saison courante par défaut
        if (!this.saison) {
          const cur = this.saisons.find((s) => s.current);
          this.saison = cur
            ? cur.id_saison
            : this.saisons.length
              ? this.saisons[0].id_saison
              : null;
        }
      })
      .catch((err) => {
        console.error('Failed to fetch saisons', err);
        this.saisons = [];
      });
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
.modele-fichier {
  margin: 1.5rem auto 0;
  width: 75%;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fafafa;
  text-align: center;
}
.modele-fichier h3 {
  margin-bottom: 0.5rem;
}
.modele-aide {
  font-size: 0.85rem;
  color: #666;
  margin: 0.4rem 0;
}
.modele-scroll {
  overflow-x: auto;
}
.modele-table {
  margin: 0 auto;
  border-collapse: collapse;
  font-size: 0.8rem;
  white-space: nowrap;
}
.modele-table th,
.modele-table td {
  border: 1px solid #ccc;
  padding: 3px 8px;
  text-align: left;
}
.modele-table th {
  background: #f1f1f1;
}
</style>
