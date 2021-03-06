import { apiRequest } from "@/core/js/data/api.js";
import { dataString } from "./functions.js";

const STORE = {
  state: {
    _areas: []
  },

  getters: {
    area: state => id_area => {return state._areas.find(n => n.id_area === id_area)},
    areas: state => id_areas => {return state._areas.find(n => id_areas.include(n.id_area))},
    areaString: (state) => (ids, key="label") => dataString(STORE, state, 'area', ids, key),
  },

  mutations: {
    areas: (state, areas) => {
      for (const area of areas) {
        if (!STORE.getters.area(state)(area.id_area)) {
          state._areas.push(area);
        }
      }
    }
  },

  actions: {
    areas: ({ commit }, id_areas) => {
      return new Promise((resolve, reject) => {
        if(!id_areas) {
          resolve();
          return 
        }
        const areasIds = Array.isArray(id_areas) ? id_areas : [id_areas];
        const params = '?' + areasIds.map(id_area => `id_area=${id_area}`).join('&')
        apiRequest("GET", `api/ref_geo/areas_simple/l${params}`).then(
          apiData => {
              const data = apiData.features.map(d => {return {...d.properties, geom: d.geom}})
            commit("areas", data);
            resolve(data);
          },
          error => {
            reject(error);
          }
        );
      });
    }
  }
};

export { STORE };
