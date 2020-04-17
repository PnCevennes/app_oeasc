import testMap from './test-map';
import testSelectMap from './test-select-map';
import testFormulaireDeclaration from './test-formulaire-declaration'


const ROUTE = [
  {
    path: '/test/map/:mapName',
    label: 'test_map',
    name: 'test_map',
    component: testMap
  },
  {
    path: '/test/select_map',
    label: 'test_select_map',
    name: 'test_select_map',
    component: testSelectMap
  },
  {
    path: '/test/form_declaration',
    label: 'test_form_declaration',
    name: 'test_form_declaration',
    component: testFormulaireDeclaration
  },
];

export { ROUTE };
