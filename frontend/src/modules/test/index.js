import genericForm from '@/components/form/generic-form'
import configFormTest from "./config/form-test.js"

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
    component: genericForm,
    props: {
      config: configFormTest
    }

  }
];

export { ROUTE };
