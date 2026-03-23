import { apiRequest } from '@/core/js/data/api.js';
import { dataString } from './functions.js';

// STORE est un objet Vuex qui gère l'état des "areas" (zones géographiques) dans l'application.
// STORE : objet Vuex qui gère l'état des "areas" (zones géographiques) dans l'application.
// Il permet de centraliser la gestion des zones, leur récupération depuis l'API, et leur accès dans les composants Vue.

const STORE = {
  state: {
    // _areas : tableau contenant les objets "area" récupérés depuis l'API.
    // Utilisé pour stocker toutes les zones chargées dans l'application.
    _areas: [],
  },

  getters: {
    // area : retourne une zone selon son id_area.
    // Utilisé pour accéder rapidement à une zone précise dans l'état, par exemple lors de l'affichage d'une fiche zone.
    area: (state) => (id_area) => {
      return state._areas.find((n) => n.id_area === id_area);
    },

    // areas : retourne les zones dont les id sont dans id_areas.
    // Utile pour récupérer plusieurs zones à la fois, par exemple pour afficher une liste de zones sélectionnées.
    areas: (state) => (id_areas) => {
      return state._areas.filter((n) => id_areas.includes(n.id_area));
    },

    // areaString : retourne une chaîne de caractères représentant une ou plusieurs zones.
    // Utilisé pour afficher les labels ou autres propriétés des zones dans l'interface utilisateur (ex : dans un tableau ou un formulaire).
    // ids : tableau ou id unique des zones à afficher.
    // key : propriété à afficher (par défaut "label").
    areaString:
      (state) =>
      (ids, key = 'label') =>
        dataString(STORE, state, 'area', ids, key),
  },

  mutations: {
    // areas : ajoute les zones reçues à l'état si elles n'existent pas déjà.
    // Utilisé après la récupération des zones depuis l'API pour mettre à jour l'état local.
    // Appelée par l'action "areas" après un commit.
    areas: (state, areas) => {
      for (const area of areas) {
        // Vérifie si la zone existe déjà avant de l'ajouter pour éviter les doublons.
        if (!STORE.getters.area(state)(area.id_area)) {
          state._areas.push(area);
        }
      }
    },
  },

  actions: {
    // areas : action asynchrone qui récupère les zones depuis l'API selon les id fournis.
    // Utilisé lors du chargement ou de la mise à jour des zones dans l'application, par exemple lors de la sélection d'une zone ou du chargement initial.
    // id_areas : tableau ou id unique des zones à récupérer.
    areas: ({ commit }, id_areas) => {
      return new Promise((resolve, reject) => {
        // Si aucun id fourni, on résout la promesse sans rien faire.
        if (!id_areas) {
          resolve();
          return;
        }
        // Prépare les paramètres pour la requête API.
        const areasIds = Array.isArray(id_areas) ? id_areas : [id_areas];
        const params = '?' + areasIds.map((id_area) => `id_area=${id_area}`).join('&');
        // Requête GET vers l'API pour récupérer les zones.
        apiRequest('GET', `api/ref_geo/areas_simple/l${params}`).then(
          (apiData) => {
            // Transforme les données reçues pour ne garder que les propriétés utiles.
            // Chaque zone récupérée contient ses propriétés et sa géométrie.
            const data = apiData.features.map((d) => {
              return { ...d.properties, geom: d.geom };
            });
            // Met à jour l'état avec les nouvelles zones via la mutation "areas".
            commit('areas', data);
            // Résout la promesse avec les données récupérées.
            resolve(data);
          },
          (error) => {
            // En cas d'erreur lors de la requête API, on rejette la promesse.
            reject(error);
          }
        );
      });
    },
  },
};

export { STORE };
