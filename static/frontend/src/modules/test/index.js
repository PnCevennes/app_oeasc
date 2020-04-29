import testMap from './test-map';


const ROUTE = [
  {
    path: '/test/map',
    label: 'Carte restitution',
    name: 'test.map',
    parent: 'test',
    access: 1,
    hideTitle: true,
    component: testMap
  },

  {
    path: '/test',
    constent: 'test',
    name: 'test',
    label: "Test",
    parent: "page.accueil",
    type: "page"
  },

];

export { ROUTE };
