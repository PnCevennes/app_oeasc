// Affiche une petite fenêtre de notification en bas de l'écran, pour informer l'utilisateur d'une action réussie ou d'une erreur.
// dans chaque vue il faudra importer le snackbarStore 
// et appeler snackbarStore.show("message à afficher", "type de message (ex: 'success' ou 'error')") pour afficher le message
// le snackbar est implémenté dans App.vue pour être accessible depuis n'importe quelle vue de l'application


import Vue from 'vue';

// Si vous êtes en Vue 2.7+, 'reactive' est intégré. 
// Sinon, on utilise Vue.observable pour la réactivité.
const state = Vue.observable({
  show: false,
  message: '',
  color: '', // couleur de fond du snackbar (ex: 'success' pour vert, 'error' pour rouge, ou une couleur personnalisée)
  timeout: 5000,
  textColor: 'black',
  fontSize: '1.3rem',
  fontWeight: 400,
  lineHeight: 1.3
  
});

export const snackbarStore = {
  // Getters pour accéder à l'état
  get state() {
    return state;
  },
  
  // Méthode pour afficher le message
  show(message, color = 'error', textColor = 'black') {
    state.message = message;
    if (color === 'success') {
      // vert très clair
      state.color = '#6fd186';
      state.textColor = 'white';
    }else if (color === 'error') {
      // rouge très clair
      state.color = '#f05d69';
      state.textColor = 'white';
    } else {
      //gris très clair
      state.color = color; // Utiliser la couleur personnalisée si fournie
      state.textColor = textColor; // Utiliser la couleur de texte personnalisée si fournie
    }

    state.show = true;
  },

  // Méthode pour fermer
  hide() {
    state.show = false;
  }
};