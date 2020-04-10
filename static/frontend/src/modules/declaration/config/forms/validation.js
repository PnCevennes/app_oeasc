const formsValidation = {
  content_validation: {
    type: "content",
    code: "declaration_validation"
  },
  content_resume: {
    type: "content",
    code: "declaration_resume",
    meta: ({ baseModel }) => ({ declaration: baseModel })
  },
  b_autorisation: {
    label:
      "J’autorise que les informations fournies dans ce formulaire soient transmises aux responsables cynégétiques locaux, pour pouvoir adapter la pression de chasse.",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    required: true
  },

  b_valid: {
    label: "Valider cette déclaration (admin seulement)",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    condition: ({ $store }) => $store.getters.droit_max >= 5
  }
};

export { formsValidation };
