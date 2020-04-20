import Vue from "vue";
import Router from "vue-router";
import { MODULES_ROUTES } from "@/modules";

Vue.use(Router);

export default new Router({
  routes: [
    ...MODULES_ROUTES.map(route => ({
      ...route,
      meta: {
        access: route.access || 0,
        content: route.content
      }
    }))
  ]
});
