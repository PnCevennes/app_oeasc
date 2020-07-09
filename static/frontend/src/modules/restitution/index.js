import testRestitution from './test-restitution';

const ROUTE = [

  {
    path: '/restitution/test',
    label: 'Restitution',
    name: 'restitution.test',
    parent: 'restitution',
    access: 1,
    hideTitle: true,
    component: testRestitution
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
