const formsValidation = {
  content_validation: {
    type: "content",
    code: "declaration_validation"
  },
  content_resume: {
    type: "content",
    code: "declaration_resume",
    meta: ({ baseModel, $store }) => ({
      declaration: baseModel,
      height: `height: ${$store.getters.declarationTableHeight || 100}px`
    })
  },
  b_autorisation: {
    label:
      "J’autorise la transmission des informations fournies aux responsables cynégétiques locaux, pour pouvoir adapter la pression de chasse.",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    required: true
  },

  b_valid: {
    label: "Valider cette déclaration (admin seulement)",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    condition: ({ $store }) => $store.getters.droitMax >= 5
  }
};

export { formsValidation };
