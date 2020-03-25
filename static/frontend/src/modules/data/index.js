import { nomenclatureActions } from './nomenclature.js'
import { apiRequest }  from '@/core/js/data/api.js';

const STORE = {
  state: {
    cache: {}
  },
  mutations: {
    // cacheKeys  exemple ["nomenclature", 'TYPE_SITE']
    setCache: (state, cacheKeys, data) => {
      let cur = state.cache;
      for (const [i, key] in cacheKeys.entries()) {
        // test si dernier element
        if (i === cacheKeys.length - 1) {
          cur[key] = data;
          return;
        }
        cur = cur[key] || {};
      }
    }
  },
  getters: {
    getFromCache: state => cacheKeys => {
      let cur = state.cache;
      for (const key of cacheKeys) {
        cur = cur[key];
        if (!cur) {
          return;
        }
        return cur;
      }
    }
  },
  actions: {
    cacheOrRequest: (
      { commit, getters },
      { url, method = 'GET', postData = null, cacheKeys, dataKeys = [] }
    ) => {
      // test if in cache
      return new Promise((resolve, reject) => {
        cacheKeys = cacheKeys || [url];
        const cacheData = getters.getFromCache(cacheKeys);
        if (cacheData) {
          resolve(cacheData);
        }

        //request and save in cache
        apiRequest(method, url, { data: postData }).then(
          apiData => {
            let curData = apiData;
            for (const key of dataKeys) {
                curData = curData[key];
            }
            commit('setCache', cacheKeys, curData);
            resolve(curData);
          },
          error => {
            reject(error);
          }
        );
      });
    }
  }
};

STORE.actions = {
    ...STORE.actions, ...nomenclatureActions
}

export { STORE };
