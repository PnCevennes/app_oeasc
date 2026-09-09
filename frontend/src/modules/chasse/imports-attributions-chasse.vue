<!--
  Page d'import du plan de chasse annuel (voir le bloc <script> pour le détail).
  Structure : 1 carte d'état « saison » + 3 blocs <import-section-attributions>
  (dates de saison / massifs / attributions), déverrouillés progressivement.
-->
<template>
  <div>
    <br />
    <h1>Import du plan de chasse</h1>
    <p style="max-width: 900px; color: #555">
      Mise à jour annuelle du plan de chasse pour la
      <strong>saison en cours</strong>
      . Les étapes se déverrouillent l'une après l'autre : chaque import n'est possible que si le
      précédent a bien alimenté la base.
    </p>

    <!-- ====================== ÉTAPE 0 : SAISON ====================== -->
    <v-card
      class="etape"
      :color="etat && etat.saison_ok ? '#e8f5e9' : '#fff3e0'"
      variant="flat"
      border
    >
      <v-card-title class="etape-titre">
        <v-icon :color="etat && etat.saison_ok ? 'green' : 'orange'">
          {{ etat && etat.saison_ok ? 'mdi-check-circle' : 'mdi-alert' }}
        </v-icon>
        1. Saison en cours
      </v-card-title>
      <v-card-text v-if="etat">
        <template v-if="etat.saison_courante">
          Saison
          <strong>{{ etat.saison_courante.nom_saison }}</strong>
          <span v-if="etat.saison_courante.date_fin">
            (fin le {{ formatDate(etat.saison_courante.date_fin) }})
          </span>
          .
        </template>
        <template v-else>Aucune saison enregistrée.</template>

        <div
          v-if="!etat.saison_ok"
          style="margin-top: 0.6rem; color: #b26a00"
        >
          <v-icon
            left
            color="orange"
          >
            mdi-arrow-right-bold
          </v-icon>
          La saison en cours est terminée (ou absente). Créez la nouvelle saison dans
          <router-link :to="{ name: 'chasse.admin' }">Données chasse → onglet Saisons</router-link>
          avant de poursuivre. Tant que ce n'est pas fait, les imports ci-dessous restent
          désactivés.
        </div>
      </v-card-text>
      <v-card-text v-else>Chargement de l'état…</v-card-text>
    </v-card>

    <!-- ============== ÉTAPE 1 : DATES DE SAISON / MODE DE CHASSE ============== -->
    <import-section-attributions
      titre="2. Dates de saison par mode de chasse"
      :active="etape1Active"
      :inactif-message="messageEtape1"
      :uploading="uploading"
      :en-cours="etapeEnCours === 'saison-dates'"
      :etape-message="etapeMessage"
      :journal="journalDe('saison-dates')"
      :exemple="exempleSaisonDates"
      texte-aide="Fichier CSV (séparateur « ; » ou « , »). Une ligne par espèce ;
        la colonne type_chasse peut contenir plusieurs modes séparés par « , »
        (une ligne de date est créée par mode). Les lignes existantes de la
        saison sont remplacées."
      @importer="(f) => lancerImport('saison-dates', f)"
    />

    <!-- ================= ÉTAPE 2 : ATTRIBUTIONS PAR MASSIF ================= -->
    <import-section-attributions
      titre="3. Attributions par massif"
      :active="etape2Active"
      :inactif-message="messageEtape2"
      :uploading="uploading"
      :en-cours="etapeEnCours === 'massifs'"
      :etape-message="etapeMessage"
      :journal="journalDe('massifs')"
      :exemple="exempleMassifs"
      texte-aide="Fichier CSV (séparateur « ; » ou « , »). La colonne saison doit
        correspondre à la saison en cours. nom_vern : Cerf / Chevreuil / Mouflon
        (les libellés « Cerf élaphe », « Chevreuil européen » sont acceptés). Les
        lignes existantes de la saison sont remplacées."
      @importer="(f) => lancerImport('massifs', f)"
    />

    <!-- ================= ÉTAPE 3 : ATTRIBUTIONS (BRACELETS) ================= -->
    <import-section-attributions
      titre="4. Attributions (bracelets)"
      :active="etape3Active"
      :inactif-message="messageEtape3"
      :uploading="uploading"
      :en-cours="etapeEnCours === 'attributions'"
      :etape-message="etapeMessage"
      :journal="journalDe('attributions')"
      :exemple="exempleAttributions"
      texte-aide="Fichier CSV (séparateur « ; » ou « , »). La colonne Annee doit
        correspondre à la saison en cours. Si la colonne zi est absente, l'id est
        extrait de TERRITOIRE (« id_zi: nom_zi »). Import incrémental : les
        nouveaux bracelets sont ajoutés, ceux qui ont disparu sont supprimés
        (sauf s'ils portent déjà une réalisation)."
      @importer="(f) => lancerImport('attributions', f)"
    />
  </div>
</template>

<script>
/**
 * Page « Import du plan de chasse » — /chasse/imports-attributions
 * (menu Administration, réservée id_droit_max >= 6).
 *
 * 3 imports CSV asynchrones séquentiels vers le backend
 * (`/api/chasse/import-attributions/<etape>`), sur le modèle de
 * `imports-chasse.vue` : POST du fichier -> réponse 202 { id_import } ->
 * polling de `import/status/<id_import>` jusqu'à TERMINE / ERREUR.
 *
 * Le déverrouillage progressif des 3 formulaires est piloté par `etat`
 * (GET `import-attributions/etat`), rechargé après chaque import réussi.
 * Un seul import à la fois : `uploading` verrouille tous les formulaires.
 */
import { apiRequest, simple_fetch } from '@/core/js/data/api.js';
import { snackbarStore } from '@/store/snackbar';
import ImportSectionAttributions from './import-section-attributions.vue';

export default {
  name: 'imports-attributions-chasse',
  components: { ImportSectionAttributions },
  data() {
    return {
      // état renvoyé par le backend : { saison_courante, saison_ok,
      // saison_dates_ok, attribution_massifs_ok, attributions_ok }
      etat: null,
      uploading: false, // un import est en cours (verrouille tous les formulaires)
      etapeEnCours: null, // 'saison-dates' | 'massifs' | 'attributions' pendant l'import
      derniereEtape: null, // dernière étape jouée (pour garder son journal affiché après coup)
      idImport: null, // id du suivi backend en cours de polling
      etapeMessage: '', // libellé « Étape n/total : … » renvoyé par le suivi
      journal: [], // lignes formatées { type, message } issues du journal backend
      pollTimer: null, // handle setTimeout du polling

      // Tableaux d'exemple affichés sous chaque formulaire (données statiques,
      // juste indicatives des colonnes attendues et de leur format).
      exempleSaisonDates: {
        colonnes: ['espece', 'date_debut', 'date_fin', 'type_chasse'],
        lignes: [
          ['Cerf', '01/09/2026', '28/02/2027', 'Approche, Affut'],
          ['Cerf', '14/09/2026', '28/02/2027', 'Battue'],
          ['Chevreuil', '14/09/2026', '28/02/2027', 'Approche, Affut, Battue'],
          ['Mouflon', '14/09/2026', '31/01/2027', 'Approche, Affut'],
        ],
      },
      exempleMassifs: {
        colonnes: ['nom_vern', 'massif', 'saison', 'nb_affecte_max', 'nb_affecte_min'],
        lignes: [
          ['Cerf élaphe', 'Aigoual nord', '2026-2027', '225', '157'],
          ['Chevreuil européen', 'Causse Méjean', '2026-2027', '93', '65'],
          ['Mouflon', 'Vallées cévenoles', '2026-2027', '0', '0'],
        ],
      },
      exempleAttributions: {
        colonnes: ['DEP', 'zi', 'TERRITOIRE', 'Espèce', 'Quantité', 'N° debut', 'N° fin', 'Annee'],
        lignes: [
          ['48', '1', '1:PNC TCA MTLO Ouest', 'CEFF', '8', '6623', '6630', '2026/2027'],
          ['48', '1', '1:PNC TCA MTLO Ouest', 'CEM', '3', '6415', '6417', '2026/2027'],
          ['48', '3', '3: ACPNC - Sect 1 - MTLO', 'CHI', '16', '6011', '6026', '2026/2027'],
        ],
      },
    };
  },
  computed: {
    // --- déverrouillage progressif : chaque étape exige la précédente -------
    saisonOk() {
      return !!(this.etat && this.etat.saison_ok);
    },
    etape1Active() {
      // dates de saison : dès qu'une saison en cours valide existe
      return this.saisonOk && !this.uploading;
    },
    etape2Active() {
      // massifs : + il faut des lignes t_saison_dates pour la saison
      return this.saisonOk && !!this.etat.saison_dates_ok && !this.uploading;
    },
    etape3Active() {
      // attributions : + il faut des lignes t_attribution_massifs
      return this.saisonOk && !!this.etat.attribution_massifs_ok && !this.uploading;
    },
    messageEtape1() {
      if (!this.saisonOk) return "Créez d'abord la nouvelle saison (étape 1).";
      if (this.uploading) return 'Un import est déjà en cours…';
      return '';
    },
    messageEtape2() {
      if (!this.saisonOk) return "Créez d'abord la nouvelle saison (étape 1).";
      if (!this.etat || !this.etat.saison_dates_ok)
        return "Importez d'abord les dates de saison par mode de chasse (étape 2).";
      if (this.uploading) return 'Un import est déjà en cours…';
      return '';
    },
    messageEtape3() {
      if (!this.saisonOk) return "Créez d'abord la nouvelle saison (étape 1).";
      if (!this.etat || !this.etat.attribution_massifs_ok)
        return "Importez d'abord les attributions par massif (étape 3).";
      if (this.uploading) return 'Un import est déjà en cours…';
      return '';
    },
  },
  methods: {
    formatDate(iso) {
      if (!iso) return '';
      const [y, m, d] = iso.split('-');
      return `${d}/${m}/${y}`;
    },

    // journal affiché sous une étape : seulement celui de l'étape en cours ou de
    // la dernière étape jouée.
    journalDe(etape) {
      return this.etapeEnCours === etape || this.derniereEtape === etape ? this.journal : [];
    },

    async chargerEtat() {
      try {
        const res = await apiRequest('GET', 'api/chasse/import-attributions/etat');
        this.etat = (res && res.etat) || null;
      } catch (err) {
        console.error('chargerEtat', err);
        snackbarStore.show("Impossible de charger l'état de l'import.", 'error');
      }
    },

    stopPolling() {
      if (this.pollTimer) {
        clearTimeout(this.pollTimer);
        this.pollTimer = null;
      }
    },

    // Envoie le fichier de l'étape et démarre le polling. `etape` est le segment
    // d'URL backend ('saison-dates' | 'massifs' | 'attributions').
    async lancerImport(etape, file) {
      if (this.uploading || !file) return;
      this.stopPolling();
      this.uploading = true;
      this.etapeEnCours = etape;
      this.derniereEtape = etape;
      this.idImport = null;
      this.etapeMessage = 'Import en attente de traitement…';
      this.journal = [];

      try {
        const formData = new FormData();
        formData.append('file', file);
        // 202 immédiat : le traitement tourne dans un thread côté serveur
        const response = await simple_fetch(
          'POST',
          `api/chasse/import-attributions/${etape}`,
          formData
        );

        if (!response) {
          // simple_fetch renvoie undefined + redirige vers /login sur un 401
          this.echec('Vous devez être connecté pour lancer un import.');
          return;
        }
        if (response.success === false || !response.id_import) {
          this.echec(response.user_message || "Erreur lors du lancement de l'import.");
          return;
        }
        this.idImport = response.id_import;
        this.pollStatus();
      } catch (err) {
        console.error('lancerImport', err);
        this.echec(err.message || "Erreur lors de l'import.");
      }
    },

    // Interroge le suivi backend toutes les 2 s jusqu'au statut final.
    async pollStatus() {
      if (!this.idImport) return;
      let res;
      try {
        res = await simple_fetch('GET', `api/chasse/import/status/${this.idImport}`);
      } catch (err) {
        // erreur réseau transitoire : on retente un peu plus tard
        console.error('pollStatus', err);
        this.pollTimer = setTimeout(() => this.pollStatus(), 3000);
        return;
      }

      if (!res || res.success === false || !res.import_status) {
        this.echec((res && res.user_message) || "Suivi de l'import indisponible.");
        return;
      }

      const st = res.import_status;
      this.journal = this.formatJournal(st.journal || []);
      this.etapeMessage = st.message || '';

      if (st.statut === 'TERMINE' || st.statut === 'ERREUR') {
        this.stopPolling();
        this.uploading = false;
        this.etapeEnCours = null;
        this.etapeMessage = '';
        if (st.statut === 'ERREUR' || st.success === false) {
          snackbarStore.show(st.message || "L'import a échoué. Voir le journal.", 'error');
        } else {
          snackbarStore.show(st.message || 'Import terminé.', 'success');
          this.chargerEtat(); // déverrouille l'étape suivante
        }
        return;
      }

      this.pollTimer = setTimeout(() => this.pollStatus(), 2000);
    },

    echec(message) {
      this.stopPolling();
      this.uploading = false;
      this.etapeEnCours = null;
      this.etapeMessage = '';
      snackbarStore.show(message, 'error');
    },

    // Le backend renvoie un journal de chaînes taguées « [INFO] … » /
    // « [ERROR] … » / « [WARNING] … » (parfois précédées d'un timestamp) ;
    // on les transforme en { type, message } pour l'affichage.
    formatJournal(journal) {
      const out = [];
      for (const log of journal) {
        if (log.includes('[ERROR]')) {
          out.push({ type: 'error', message: log.replace(/^.*\[ERROR\]\s?/, '') });
        } else if (log.includes('[WARNING]')) {
          out.push({ type: 'warning', message: log.replace(/^.*\[WARNING\]\s?/, '') });
        } else if (log.includes('[INFO]')) {
          out.push({ type: 'info', message: log.replace(/^.*\[INFO\]\s?/, '') });
        }
      }
      return out.slice(-300);
    },
  },

  mounted() {
    this.chargerEtat();
  },

  beforeUnmount() {
    this.stopPolling();
  },
};
</script>

<style scoped>
.etape {
  max-width: 1000px;
  margin: 0 0 1.25rem 0;
  padding-bottom: 0.5rem;
}
.etape-titre {
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
