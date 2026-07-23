// Ce module est importé de façon statique par modules/index.js pour TOUTES les pages
// (construction du store Vuex central), pas seulement celles avec une carte. Ne pas importer
// MapService ici : ce fichier charge Leaflet/leaflet-easyprint/tous les map-elements en tête
// (voir map-service.js), ce qui ferait charger Leaflet sur chaque page de l'app. base-map.vue
// importe MapService directement depuis './map-service.js'.

// Définition de l'objet STORE qui gère l'état des services de carte
const STORE = {
  state: {
    // Stockage des instances MapService, indexées par leur identifiant
    _mapServices: {},
  },
  getters: {
    // Retourne une instance MapService selon la clé fournie
    mapService: (state) => (key) => {
      return state._mapServices[key];
    },
    // Retourne toutes les instances MapService associées aux éléments DOM ayant la classe "map" dans un conteneur donné
    elemMapServices: (state) => (id) => {
      return Object.values(
        // Récupère tous les éléments ayant la classe "map" dans l'élément dont l'id est fourni
        document.getElementById(id).getElementsByClassName('map') || {}
      ).map((elem) =>
        // Pour chaque élément, récupère le MapService correspondant à son id
        STORE.getters.mapService(state)(elem.id)
      );
    },
  },
  mutations: {
    // Ajoute ou met à jour une instance MapService dans l'état
    setMapService: (state, mapService) => {
      state._mapServices[mapService._id] = mapService;
    },
    // Retire une instance MapService de l'état (appelé au démontage du composant base-map)
    removeMapService: (state, id) => {
      delete state._mapServices[id];
    },
  },
  actions: {},
};

export { STORE };
