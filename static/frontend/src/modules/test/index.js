import testMap from './test-map';


const ROUTE = [
  {
    path: '/test/map/:mapName',
    label: 'test_map',
    name: 'test_map',
    access: 1,
    hideTitle: true,
    component: testMap
  },
];

export { ROUTE };
