/**
 * Restitution2
 *
 * nouvelle version 'server side'
 *
 * dataType
 *  - 'chasse' : données chasse (en cours)
 *
 * ROUTE :
 *  - composant : RestitutionDashboard
 *    - pour construire les graphiques à partir de paramètress
 *    - récupérer le code du widget pour le mettre dans du contenu
 *
 * STORE :
 *  - actions
 *    - restitutionCustom : requete pour récupérer les données pour les graphes (fonction de params)
 *
 * TODO :
 *   - display : tableau et cartes
 *   - options (pouvoir refaire comme la restitution des déclarations):
 *     - nb_max (comment le gérer en sql)
 *     - fieldName2 (pour les graphique en cascade)
 *
*/

import RestitutionDashboard from './restitution-dashboard.vue';

import { apiRequest } from "@/core/js/data/api.js";

const ROUTE = [
    {
      path: '/restitution2/test',
      label: 'Restitution (nouvelle version) - tableau de bord',
      name: 'restitution2.test',
      access: 1,
      hideTitle: true,
      component: RestitutionDashboard,
    }
  ]

const STORE = {
  actions: {
    /**
     * effectue une requete pour les resultats génériques
     */
    restitutionCustom: ({ getter }, params) => {
      getter;
      return apiRequest("GET", `api/resultat/custom/`, { params });
    }
  }
}

export { ROUTE, STORE }