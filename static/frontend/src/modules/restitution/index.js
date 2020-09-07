import RestitutionTest from './restitution-test.vue';

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

export { ROUTE };
