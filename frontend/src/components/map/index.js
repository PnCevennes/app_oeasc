import { MapService } from "./map-service.js";

// Définition de l'objet STORE qui gère l'état des services de carte
const STORE = {
  state: {
    // Stockage des instances MapService, indexées par leur identifiant
    _mapServices: {}
  },
  getters: {
    // Retourne une instance MapService selon la clé fournie
    mapService: state => key => {
      return state._mapServices[key];
    },
    // Retourne toutes les instances MapService associées aux éléments DOM ayant la classe "map" dans un conteneur donné
    elemMapServices: state => (id) => {
      return Object.values(
        // Récupère tous les éléments ayant la classe "map" dans l'élément dont l'id est fourni
        document.getElementById(id).getElementsByClassName("map") || {}
      ).map(elem => 
        // Pour chaque élément, récupère le MapService correspondant à son id
        STORE.getters.mapService(state)(elem.id)
      );
    }
  },
  mutations: {
    // Ajoute ou met à jour une instance MapService dans l'état
    setMapService: (state, mapService) => {
      state._mapServices[mapService._id] = mapService;
    }
  },
  actions: {}
};

export { STORE, MapService };
