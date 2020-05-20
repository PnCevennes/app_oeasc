import Vue from "vue";
import App from "./App.vue";
import router from "@/router";
import store from "@/store/store";

import vuetify from "@/plugins/vuetify"; // path to vuetify export
import VueSession from "vue-session";


Vue.config.productionTip = false;
Vue.config.devServer = { port: 8080, proxy: "http://localhost:5000" };

Vue.use(VueSession, { persist: true });

Vue.use(vuetify);

new Vue({
  router,
  store,
  vuetify,
  VueSession,
  render: h => h(App)
}).$mount("#app");
