import { postDeclaration } from "../declarations";

const sessionsValidation = {
  validation: {
    title: "Validation",
    groups: {
      content: {
        class: ['no-border'],
        forms: ["content_validation"]
      },
      autorisation: {
        forms: ["b_autorisation"]
      },
      validation: {
        forms: ["b_valid"]
      }
    },
    action: {
      label: "valider",
      process: postDeclaration
    }
  },
};

export { sessionsValidation };
