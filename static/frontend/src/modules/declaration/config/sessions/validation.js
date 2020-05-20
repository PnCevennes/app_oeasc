import { postDeclaration } from "../declarations";

const sessionsValidation = {
  validation: {
    title: "Validation",
    groups: {
      content_validation: {
        class: ["no-border"],
        forms: ["content_validation"]
      },
      autorisation: {
        forms: ["b_autorisation"]
      },
      content_resume: {
        class: ["no-border"],
        forms: ["content_resume"]
      },

      validation: {
        forms: ["b_valid"]
      }
    },
    action: {
      label: "valider",
      process: postDeclaration
    }
  }
};

export { sessionsValidation };
