import { STORE as nomenclatureStore } from './nomenclature.js';
import { STORE as areaStore } from './area.js';

const STORE = {};
const stores = [nomenclatureStore, areaStore];

for (const store of stores) {
  for (const key in store) {
    if (!(key in STORE)) {
      STORE[key] = {};
    }
    STORE[key] = { ...STORE[key], ...store[key] };
  }
}

export { STORE };
