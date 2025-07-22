import { MapService } from "./map-service.js";

const STORE = {
  state: {
    _mapServices: {}
  },
  getters: {
    mapService: state => key => {
      return state._mapServices[key];
    },
    elemMapServices: state => (id) => {
      return Object.values(
        document.getElementById(id).getElementsByClassName("map") || {}
      ).map(elem => STORE.getters.mapService(state)(elem.id));
    }
  },
  mutations: {
    setMapService: (state, mapService) => {
      state._mapServices[mapService._id] = mapService;
    }
  },
  actions: {}
};

export { STORE, MapService };
