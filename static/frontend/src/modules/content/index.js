import content from './content';

const ROUTE = [
  {
    path: '/',
    label: 'accueil',
    access: [],
    name: 'accueil',
    component: content
  },
  {
    path: '/content/:code',
    label: 'content',
    access: [],
    name: 'content',
    component: content
  }
];

export { ROUTE, content };
