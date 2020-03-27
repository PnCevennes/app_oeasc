const formsValidation = {
    content_validation: {
        type: 'content',
        code: 'declaration_validation'
    },
    validation: {
    label:
      "J’autorise que les informations fournies dans ce formulaire soient transmises aux responsables cynégétiques locaux, pour pouvoir adapter la pression de chasse.",
    type: "bool_radio",
    labels: ["Oui", "Non"],
    required: true
  }
};

export { formsValidation };
