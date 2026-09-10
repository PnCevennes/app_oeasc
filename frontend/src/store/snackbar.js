// Affiche une notification globale en bas de l'écran, pour informer l'utilisateur d'une action
// réussie, d'une info ou d'une erreur.
//
// Utilisation depuis n'importe quelle vue :
//   import { snackbarStore } from '@/store/snackbar.js';
//   snackbarStore.show('Message à afficher', 'error');   // 'error' | 'success' | 'info' | 'warning'
//
// Le rendu (styles, icône, couleurs) est géré dans App.vue à partir de `state.type`.
// Le snackbar est monté une seule fois dans App.vue pour être accessible partout.

import { reactive } from 'vue';

// Types sémantiques reconnus -> icône mdi associée.
const TYPES = {
  success: 'mdi-check-circle',
  error: 'mdi-alert-circle',
  info: 'mdi-information',
  warning: 'mdi-alert',
};

const DEFAULT_TIMEOUT = 5000;

const state = reactive({
  show: false,
  message: '',
  type: 'info', // 'success' | 'error' | 'info' | 'warning' | 'custom'
  icon: TYPES.info,
  timeout: DEFAULT_TIMEOUT,
  // Utilisés uniquement quand une couleur personnalisée est passée (type === 'custom')
  customColor: '',
  customTextColor: '',
});

export const snackbarStore = {
  get state() {
    return state;
  },

  /**
   * Affiche le snackbar.
   * @param {string} message  Texte à afficher (les retours à la ligne sont conservés).
   * @param {string} type     'error' (défaut) | 'success' | 'info' | 'warning', ou une
   *                           couleur CSS personnalisée (rétro-compat).
   * @param {string} textColor Couleur du texte si `type` est une couleur personnalisée.
   * @param {object} options   { timeout } — durée d'affichage en ms.
   */
  show(message, type = 'error', textColor = '', options = {}) {
    state.message = message;
    state.timeout = options.timeout ?? DEFAULT_TIMEOUT;

    if (TYPES[type]) {
      state.type = type;
      state.icon = TYPES[type];
      state.customColor = '';
      state.customTextColor = '';
    } else {
      // Rétro-compatibilité : une couleur CSS arbitraire a été passée.
      state.type = 'custom';
      state.icon = TYPES.info;
      state.customColor = type;
      state.customTextColor = textColor || 'white';
    }

    state.show = true;
  },

  hide() {
    state.show = false;
  },
};
