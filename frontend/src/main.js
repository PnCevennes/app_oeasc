import Vue from "vue";
import App from "./App.vue";
import router from "@/router";
import store from "@/store/store";

import vuetify from "@/plugins/vuetify"; // path to vuetify export
import VueSession from "vue-session";

import Highcharts from 'highcharts'
import More from 'highcharts/highcharts-more'
import exporting from 'highcharts/modules/exporting';
import HighchartsVue from 'highcharts-vue'

More(Highcharts);
exporting(Highcharts);

Vue.config.productionTip = false;
Vue.config.devServer = { port: 8080, proxy: "http://localhost:5000" };

Vue.use(VueSession, { persist: true });

Vue.use(vuetify);
Vue.use(HighchartsVue, {
	highcharts: Highcharts
})

new Vue({
  router,
  store,
  vuetify,
  VueSession,
  render: h => h(App)
}).$mount("#app");
