import Vue from "vue";
import Router from "vue-router";
import {page} from "@/modules/page"
import { MODULES_ROUTES } from "@/modules";

Vue.use(Router);

export default new Router({
  routes: [
    ...MODULES_ROUTES.map(route => {
      const defaultConfig =
        route.type == "page"
          ? {
              component: page
            }
          : {};
      return {
        ...defaultConfig,
        ...route,
        meta: {
          access: route.access || 0,
          content: route.content,
          hideTitle: route.hideTitle,
          label: route.label,
        }
      };
    })
  ]
});
