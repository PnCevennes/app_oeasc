import { simple_fetch } from '@/core/js/data/api.js';

// Nombre d'échecs réseau consécutifs du polling avant d'abandonner (~1 min à 3 s d'intervalle)
const MAX_POLL_FAILURES = 20;

/**
 * Import CSV asynchrone : POST du fichier -> réponse 202 { id_import } -> polling de
 * `statusUrl(idImport)` jusqu'au statut TERMINE / ERREUR.
 *
 * Le composant fournit :
 *  - statusUrl(idImport)            : URL relative du suivi (ex. `api/chasse/import/status/${id}`)
 *  - onImportProgress(st)           : à chaque poll, st = import_status (journal, message…)
 *  - onImportFinished(st, hasError) : statut final atteint (polling déjà arrêté)
 *  - onImportError(message)         : échec de lancement / de suivi (polling déjà arrêté)
 * et appelle `startAsyncImport(url, formData)`.
 */
export const asyncImportMixin = {
  data() {
    return {
      idImport: null, // id de la ligne de suivi de l'import lancé en tâche de fond
      etapeMessage: '', // libellé de l'étape en cours (ex. "Étape 4/11 : ...")
      pollTimer: null,
      pollFailures: 0,
    };
  },
  methods: {
    stopPolling() {
      if (this.pollTimer) {
        clearTimeout(this.pollTimer);
        this.pollTimer = null;
      }
    },

    // remet à zéro le suivi (à appeler avant un nouvel import ou sur « annuler »)
    resetAsyncImport() {
      this.stopPolling();
      this.pollFailures = 0;
      this.idImport = null;
      this.etapeMessage = '';
    },

    // Lancement : le backend enregistre le fichier, crée une ligne de suivi et traite en
    // tâche de fond. Réponse immédiate (202) avec id_import.
    async startAsyncImport(url, formData) {
      this.resetAsyncImport();
      try {
        const response = await simple_fetch('POST', url, formData);
        // simple_fetch redirige vers #/login et retourne undefined en cas de 401
        if (!response) {
          this.failAsyncImport('Vous devez être connecté pour importer un fichier.');
          return;
        }
        if (response.success === false || !response.id_import) {
          this.failAsyncImport(response.user_message || "Erreur lors du lancement de l'import.");
          return;
        }
        this.idImport = response.id_import;
        this.etapeMessage = 'Import en attente de traitement…';
        this.pollStatus();
      } catch (err) {
        console.error("Erreur lors de l'import:", err);
        this.failAsyncImport(err.message || "Erreur lors de l'import.");
      }
    },

    failAsyncImport(message) {
      this.stopPolling();
      this.etapeMessage = '';
      this.onImportError(message);
    },

    // interroge périodiquement l'état de l'import jusqu'à TERMINE / ERREUR
    async pollStatus() {
      if (!this.idImport) return;
      let res;
      try {
        res = await simple_fetch('GET', this.statusUrl(this.idImport));
      } catch (err) {
        console.error('pollStatus:', err);
        // erreur réseau : on retente, mais pas indéfiniment
        this.pollFailures += 1;
        if (this.pollFailures >= MAX_POLL_FAILURES) {
          this.pollFailures = 0;
          this.failAsyncImport('Suivi de l’import interrompu : serveur injoignable.');
          return;
        }
        this.pollTimer = setTimeout(() => this.pollStatus(), 3000);
        return;
      }

      this.pollFailures = 0;
      if (!res || res.success === false || !res.import_status) {
        this.failAsyncImport((res && res.user_message) || "Suivi de l'import indisponible.");
        return;
      }

      const st = res.import_status;
      this.onImportProgress(st);
      this.etapeMessage = st.message || '';

      if (st.statut === 'TERMINE' || st.statut === 'ERREUR') {
        this.stopPolling();
        this.etapeMessage = '';
        this.onImportFinished(st, st.statut === 'ERREUR' || st.success === false);
        return;
      }

      this.pollTimer = setTimeout(() => this.pollStatus(), 2000);
    },
  },

  beforeUnmount() {
    // stoppe le polling si l'utilisateur quitte la page pendant un import
    this.stopPolling();
  },
};

/**
 * Case « mettre à jour les données existantes » avec popup de confirmation
 * (imports chasse et dégâts agricoles).
 */
export const updatePopupMixin = {
  data() {
    return {
      doUpdate: false,
      affiche_popup_update: false, // etat de la checkbox
    };
  },
  methods: {
    close_popup_update() {
      // ferme la popup de confirmation et décoche la checkbox
      this.doUpdate = false;
      this.affiche_popup_update = false;
    },

    afficherPopup() {
      if (this.doUpdate == true) {
        this.affiche_popup_update = true;
      }
    },

    confirmUpdate_action() {
      // la personne confirme la mise à jour dans la popup
      this.affiche_popup_update = false;
      this.doUpdate = true;
    },
  },
};

// Reconstruit la liste { type, message } d'un journal de lignes taguées [ERROR] / [INFO] /
// [WARNING] / [FILE]. Idempotent : appelé à chaque poll.
export const parseJournal = (journal, maxDisplay = 1000) => {
  const lines = Array.isArray(journal) ? journal : [];
  const out = [];
  let fichierErreur = null;
  for (const log of lines) {
    if (log.includes('[ERROR]')) {
      out.push({ type: 'error', message: log.replace('[ERROR] ', '') });
    } else if (log.includes('[INFO]')) {
      out.push({ type: 'info', message: log.replace('[INFO] ', '') });
    } else if (log.includes('[WARNING]')) {
      out.push({ type: 'warning', message: log.replace('[WARNING] ', '') });
    } else if (log.includes('[FILE]')) {
      fichierErreur = log.replace('[FILE] ', '');
      out.push({ type: 'file', message: fichierErreur });
    }
  }
  return { lignes: out.length > maxDisplay ? out.slice(-maxDisplay) : out, fichierErreur };
};
