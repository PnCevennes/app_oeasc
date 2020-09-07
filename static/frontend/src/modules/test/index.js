import testForm from "./test-form.vue";

const ROUTE = [
  {
    path: "/test",
    content: "test",
    name: "test",
    label: "restitution - Test",
    parent: "page.accueil",
    type: "page"
  },
  {
    path: "/test/form",
    name: "test.form",
    label: "Test Form",
    parent: "test",
    component: testForm
  }
];

export { ROUTE };
