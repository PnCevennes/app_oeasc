import Vue from 'vue';
import Router from 'vue-router';
// import {
//     Login,
//     Logout,
//     Err404
// } from '@/core/'
// import {CORE_MODULES} from '@/core'
import { MODULES_ROUTES } from '@/modules';

Vue.use(Router);

export default new Router({
  routes: [...MODULES_ROUTES]
});
