import { postDeclaration } from "../declarations";

const sessionsValidation = {
  validation: {
    title: "validation",
    groups: {
      validation: {
        forms: ["content_validation", "b_autorisation"]
      }
    },
    action: {
      label: "valider",
      process: postDeclaration
    }
  },
};

export { sessionsValidation };
