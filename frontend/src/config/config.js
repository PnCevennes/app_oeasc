import frontend from 'virtual:config-frontend'; // généré depuis install/config_principal.yaml (voir vite.config.js)
import { configMap, preConfigMap } from './config-map';

const config = {
  URL_APPLICATION: frontend.URL_APPLICATION,
  URL_FRONTEND: frontend.URL_FRONTEND,
  ID_APPLICATION: frontend.ID_APPLICATION,
  MATOMO: frontend.MATOMO,
  map: configMap,
  preConfigMap,
};

export { config };
