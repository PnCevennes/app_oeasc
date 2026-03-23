<!-- <template>
  <div>
    <br></br>
    <h1>Importation des données Chasse</h1>
    <br></br>

    <v-row>

      <v-col cols="12" sm="6">
        <v-select
          :value="selectedSaison"
          @input="saison = $event"
          :items="saisons"
          item-text="nom_saison"
          item-value="id_saison"
          label="Saison"
          dense
          outlined
          clearable
        ></v-select>
      </v-col>

      <v-col cols="12" sm="6" class="d-flex align-center">
        <v-checkbox
          :input-value="update_data_bdd ? true : doUpdate"
          @change="val => { if (val) { update_data_bdd = true } else { doUpdate = false; update_data_bdd = false } }"
          label="Mettre à jour les données existantes"
          hide-details
        ></v-checkbox>
      </v-col>

    </v-row>

    <v-file-input
      v-model="file"
      label="Sélectionner un fichier CSV"
      accept=".csv"
      outlined
      dense
      hide-details
    ></v-file-input>

    <div class="mt-2">
      <v-btn :disabled="!file || uploading" color="primary" @click="validateUpload">
        <v-icon left>mdi-upload</v-icon>
        Importer
      </v-btn>
      <v-btn text @click="clear" :disabled="uploading">Annuler</v-btn>
    </div>

    <v-progress-linear v-if="uploading" indeterminate color="primary" class="mt-3"></v-progress-linear>

    <div v-if="message" class="mt-3">
      <div v-if="error" style="color:crimson">{{ message }}</div>
      <div v-else style="color:green">{{ message }}</div>
    </div>

    <div>
      <pre>{{ json_data_bdd }}</pre>
      <table>
        <thead>
          <tr>
            <th>id</th>
            <th>BRACELET</th>
            <th>ESPECE</th>
            <th>AGE</th>
            <th>DATE</th>
          </tr>
        </thead>

      </table>
      
    </div>



    <v-dialog v-model="update_data_bdd" max-width="500">
      <v-card>
        <v-card-title class="headline">Confirmer la mise à jour</v-card-title>
        <v-card-text>Vous avez demandé une mise à jour des données existantes. Les données seront écrasées et aucun retour en arrière ne sera possible. Confirmez-vous l'opération ?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red" text @click="update_data_bdd = false">NON Annuler</v-btn>
          <v-btn color="green" text @click="confirmUpdate_action">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template> -->

<!-- <script>
import { apiRequest } from "@/core/js/data/api.js";

export default {
  name: "imports-chasse",
  data() {
    return {
      file: null,
      uploading: false,
      message: '',
      json_data_bdd: null,
      error: false,
      saisons: [],
      saison: null,
      doUpdate: false,
      update_data_bdd: false // etat de la checkbox 
    };
  },
  methods: {
    clear() {
      // réinitialise tout si la personne clic sur annuler
      this.file = null;
      this.message = '';
      this.error = false;
      this.doUpdate = false;
    },

    validateUpload() {
      // action finale, une fois que l'utilisateur a cliqué sur le bouton IMPORTER. 
      if (this.doUpdate) {
        this.update_data_bdd = true;
        return;
      }
      this.upload();
    },

    confirmUpdate_action() {
      // Si la personne confirme la mise à jour dans la popup, on passe doUpdate à true
      this.update_data_bdd = false;
      this.doUpdate = true;

    },

    async upload() {
      // action finale. Envoie le fichier à l'API pour traitement et attend la réponse pour afficher le message de succès ou d'erreur

      if (!this.file) {
        this.message = 'Aucun fichier sélectionné.';
        this.error = true;
        return;
      }

      this.uploading = true;
      this.message = '';
      this.error = false;

      try {
        // apiRequest supports File in postData and builds FormData
        const postData = { file: this.file };
        if (this.saison) postData.saison = this.saison;
        postData.update = this.doUpdate ? true : false;

        const res = await apiRequest('POST', 'api/chasse/import/traitement-csv', { postData }).then(res => {
          console.log('API response for import:', res);
          this.message = res.message || 'Importation réussie.';
          this.json_data_bdd = res.json_data_bdd || null; // afficher les données retournées par l'API
          return res;
        }).catch(err => {
          console.error('API error during import', err);
          throw err; // rethrow pour être catché par le catch externe
        });


      } catch (err) {
        console.error('Import CSV failed', err);
        this.message = (err && err.message) ? err.message : 'Erreur lors de l\'import.';
        this.error = true;
      } finally {
        this.uploading = false;
      }
    }
  },

  computed: {
    selectedSaison() {
      // retourne la saison dont current=true pour mettre par défaut la saison en cours
      if (this.saison) return this.saison;
      const cur = this.saisons.find(s => s.current);
      return cur ? cur.id_saison : null;
    }
  },

  mounted() {
      // récupérer les saisons disponibles via l'API
      apiRequest('GET', 'api/generic/chasse/saisons/').then(res => {
        console.log('API response for saisons:', res);
        this.saisons = res.items || [];
        // tri this saison par ordre décroissant d'id (du plus récent au plus ancien)
        this.saisons.sort((a, b) => b.id_saison - a.id_saison);
        console.log('Saisons chargées', this.saisons);
      }).catch(err => {
        console.error('Failed to fetch saisons', err);
        this.saisons = [];
      });
    }


  };

</script> -->

<!-- <style scoped>
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }
</style> -->
