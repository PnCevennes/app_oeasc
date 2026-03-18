<template>
  <div>
    <br />
    <h1>Importation des données Chasse</h1>
    <br />

    <div :disabled="uploading">
      <div style="max-width: 500px">
        <!-- formulaire select pour la saison, affiche la saison en cours par défaut -->
        <v-select
          v-model="saison"
          :items="saisons"
          item-text="nom_saison"
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
        <div class="mt-2">
          <v-btn
            :disabled="!file || uploading"
            color="primary"
            @click="upload"
          >
            <v-icon left>mdi-upload</v-icon>
            Importer
          </v-btn>
          <v-btn
            text
            @click="clear"
            :disabled="uploading"
          >
            Annuler
          </v-btn>
        </div>
      </div>
    </div>

    <v-progress-linear
      v-if="uploading"
      indeterminate
      color="primary"
      class="mt-3"
    ></v-progress-linear>

    <!-- affichage des messages de succès ou d'erreur après l'import -->
    <!-- <div v-if="message" class="mt-3">
      <div v-if="error" style="color:crimson">{{ message }}</div>
      <div v-else style="color:green">{{ message }}</div>
    </div> -->

    <!-- affichage de json_data_bdd sous forme du tableau -->
    <div
      style="margin-top: 1rem; max-width: 70%"
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
            v-for="value in reponse_affichee"
            :key="value.message"
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
              <span v-if="value.type === 'file'">
                Un fichier à été généré:
                <a
                  :href="create_url_fichier_erreur(value.message)"
                  target="_blank"
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
            text
            @click="close_popup_update"
          >
            NON Annuler
          </v-btn>
          <v-btn
            color="green"
            text
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
import { apiRequest, simple_fetch, url } from '@/core/js/data/api.js';

export default {
  name: 'imports-chasse',
  data() {
    return {
      file: null,
      uploading: false,
      message: '',
      // json_data_bdd: null,
      reponse_affichee: [],
      error: false,
      saisons: [],
      saison: null,
      doUpdate: false,
      affiche_popup_update: false, // etat de la checkbox
      nom_fichier_erreur: null, // si il est différent de null, on propose un bouton de téléchargement du fichier d'erreur généré par le backend
      url_fichier_erreur: null,
    };
  },
  methods: {
    clear() {
      // réinitialise tout si la personne clic sur annuler
      this.file = null;
      this.message = '';
      this.error = false;
      this.doUpdate = false;
      this.affiche_popup_update = false;
      this.reponse_affichee = [];
      this.nom_fichier_erreur = null;
      this.url_fichier_erreur = null;
      this.response;
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

      this.message = '';
      this.error = false;
      this.reponse_affichee = [];
      this.nom_fichier_erreur = null;
      this.url_fichier_erreur = null;

      try {
        this.uploading = true;
        const formData = new FormData();
        formData.append('file', this.file);
        formData.append('update', this.doUpdate.toString());

        if (this.saison) {
          formData.append('saison', this.saison);
        }
        formData.append('id_role', this.$store.getters.user.id_role); // à remplacer par le rôle de l'utilisateur connecté, ici on met 1 pour les tests
        formData.append('nom_complet', this.$store.getters.user.nom_complet); // à remplacer par le nom complet de l'utilisateur connecté, ici on met "Test User" pour les tests

        // console.log('Envoi du FormData...');

        const response = await simple_fetch('POST', 'api/chasse/import/traitement-csv', formData);
        console.log("Réponse brute de l'API:", response);
        this.traitement_journal(response);
        // this.message = response.journal || 'Importation réussie.';
        console.log('Réponse API:', response.journal);
        this.uploading = false;
      } catch (err) {
        console.error("Erreur lors de l'import:", err);
        this.message = err.message || "Erreur lors de l'import.";
        this.error = true;
        this.uploading = false;
      } finally {
        this.uploading = false;
      }
    },

    traitement_journal(response) {
      // parcours les lignes du journal pour remplir le dic reponse_affichee qui aura logo et message à chaque lignes.
      // si la ligne contient [ERROR] on met un icone de croix rouge
      // si la ligne contient [INFO] on met un icone de check vert
      // si la ligne contient [FILE] on créé icone de fichier et nom_fichier_erreur prendra la valeur du nom du fichier d'erreur à télécharger
      // message contiendra le message sans les tags [ERROR], [INFO] ou [FILE]

      for (let log of response.journal) {
        if (log.includes('[ERROR]')) {
          this.reponse_affichee.push({ type: 'error', message: log.replace('[ERROR] ', '') });
        } else if (log.includes('[INFO]')) {
          this.reponse_affichee.push({ type: 'info', message: log.replace('[INFO] ', '') });
        } else if (log.includes('[FILE]')) {
          const fileName = log.replace('[FILE] ', '');
          this.nom_fichier_erreur = fileName; // stocke le nom du fichier d'erreur pour afficher le bouton de téléchargement
          this.reponse_affichee.push({ type: 'file', message: fileName });
          // this.urlCSV(); // génère l'URL du fichier d'erreur à partir du nom du fichier fourni par le backend
        }
      }
      return this.reponse_affichee;
    },

    create_url_fichier_erreur(nom_fichier) {
      if (!nom_fichier) {
        console.error("Aucun fichier d'erreur disponible pour le téléchargement.");
        return null;
      }
      this.url_fichier_erreur = url(
        `api/chasse/import/download-erreurs-csv/${nom_fichier}`
      ).toString();
      return this.url_fichier_erreur;
    },

    // urlCSV() {
    //   if (!this.nom_fichier_erreur) {
    //     console.error('Aucun fichier d\'erreur disponible pour le téléchargement.');
    //     return null;
    //   }
    //   this.url_fichier_erreur = url(`api/chasse/import/download-erreurs-csv/${this.nom_fichier_erreur}`).toString();
    //   return this.url_fichier_erreur;

    // }
  },

  computed: {},

  mounted() {
    // récupérer les saisons disponibles via l'API
    apiRequest('GET', 'api/generic/chasse/saisons/')
      .then((res) => {
        // console.log('API response for saisons:', res);
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
        // console.log('Saisons chargées', this.saisons);
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
</style>
