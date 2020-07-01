import testMap from './test-map';
import testRestitution from './test-restitution';


const ROUTE = [
  {
    path: '/test/map/restitution',
    label: 'Carte restitution',
    name: 'test.map',
    parent: 'test',
    access: 1,
    hideTitle: true,
    component: testMap
  },

  {
    path: '/test/restitution',
    label: 'Restitution',
    name: 'test.restitution',
    parent: 'test',
    access: 1,
    hideTitle: true,
    component: testRestitution
  },


  {
    path: '/test',
    content: 'test',
    name: 'test',
    label: "Test",
    parent: "page.accueil",
    type: "page"
  },

];

export { ROUTE };
