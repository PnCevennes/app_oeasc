import restitution from './restitution.vue';

const ROUTE = [

  {
    path: '/restitution/test',
    label: 'Test',
    name: 'restitution.test',
    parent: 'restitution',
    access: 1,
    hideTitle: true,
    component: restitution
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
