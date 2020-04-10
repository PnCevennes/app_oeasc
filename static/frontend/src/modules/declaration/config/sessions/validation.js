import { postDeclaration } from "../declarations";

const sessionsValidation = {
  validation: {
    title: "Validation",
    groups: {
      content: {
        class: ['no-border'],
        forms: ["content_validation"]
      },
      validation: {
        forms: ["b_autorisation"]
      }
    },
    action: {
      label: "valider",
      process: postDeclaration
    }
  },
};

export { sessionsValidation };
