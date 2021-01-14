import RestitutionTest from './restitution-dashboard.vue';
import Vue from 'vue';
const ROUTE = [

  {
    path: '/restitution/test',
    label: 'Restitution - tableau de bord',
    name: 'restitution.test',
    parent: 'restitution',
    access: 1,
    hideTitle: true,
    component: RestitutionTest,
  },
  {
    path: '/restitution',
    content: 'restitution',
    name: 'restitution',
    label: "Restitution",
    parent: "page.accueil",
    type: "page"
  },

];

const STORE = {
  state: {
    _restitutionDataCount: {}
  },
  getters: {
    restitutionDataCount: state => dataType => {
      return state._restitutionDataCount[dataType];
  },
},
  mutations: { 
    restitutionDataCount: (state, {dataType, count}) => {
      // pb reactivité
      // https://forum.vuejs.org/t/forcing-a-refresh-to-a-getter/32922/4
      // state._restitutionDataCount[dataType] = count;
      Vue.set(state._restitutionDataCount, dataType, count);
    }
  }
}
  
export { ROUTE, STORE };
