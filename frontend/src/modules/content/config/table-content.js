import configContentForm from "./form-content";

export default {
  storeName: "commonsContent",
  dense: true,
  striped: true,
  small: true,
  configForm: configContentForm,
  headerDefs: {
    id_content: {
      text: "Id"
    },
    code: {
      text: "Code"
    },
    tags: {
      text: "Tags",
      display: (d) => d && d.length ? d.map(d => d.nom_tag).join(', ') : ''
    },
    md: {
      text: "MarkDown",
    },

    link: {
      text: 'Lien',
      preProcess: (d) => d.code,
      display: d => `<a href="#/content/${d}" target="_blank  ">${d}</a>`,
    }
  },
  sortBy: ["nom_content"],
  sortDesc: [true],
  label: 'nom_content',
};
