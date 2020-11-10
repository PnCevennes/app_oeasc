import formDefsForet from "./forms/foret";
import formDefsPeuplement from "./forms/peuplement";
import formDefsDegat from "./forms/degat";
import formDefsCommentaires from "./forms/commentaires.js";
import formDefsValidation from "./forms/validation";

import sessionDefsForet from "./sessions/foret";
import sessionDefsPeuplement from "./sessions/peuplement";
import sessionDefsDegat from "./sessions/degat";
import sessionDefsCommentaires from "./sessions/commentaires";
import sessionDefsValidation from "./sessions/validation";

const formDefs = {
  ...formDefsForet,
  ...formDefsPeuplement,
  ...formDefsDegat,
  ...formDefsCommentaires,
  ...formDefsValidation
};

const sessionDefs = {
  ...sessionDefsForet,
  ...sessionDefsPeuplement,
  ...sessionDefsDegat,
  ...sessionDefsCommentaires,
  ...sessionDefsValidation
};

export default {
  help: "declaration_help",
  action: {
    request: {
      method: "POST",
      url: "api/degat_foret/declaration"
    }
  },
  preloadData: ({ $store, id, config }) => {
    return new Promise(resolve => {
      const promises = [
        $store.dispatch("nomenclatures"),
        id &&
          $store.dispatch("declarationForm", id)
      ];

      Promise.all(promises).then(() => {
        let declaration = id
          ? $store.getters.declarationForm
          : {};
        declaration = { ...declaration.foret, ...declaration };

        ///
        // this.declaration = configDeclaration.initModel(declaration);

        declaration.id_declarant =
          declaration.id_declarant || $store.getters.user.id_role;

        config.value = declaration;
        resolve();
      });
    });
  },
  title: ({ id }) =>
    id
      ? `Modifier la déclaration ${id}`
      : "Signaler des dégâts de grand gibier en forêt",
  formDefs,
  sessionDefs,
  sessionGroups: {
    foret: {
      title: "Informations sur la forêt",
      sessions: [
        "foret_statut",
        "foret_localisation",
        "foret_informations",
        "foret_proprietaire"
      ]
    },
    peuplement: {
      title: "Informations sur le peuplement",
      sessions: [
        "peuplement_localisation",
        "peuplement_description",
        "peuplement_protection",
        "peuplement_paturage",
        "peuplement_autres"
      ]
    },
    degats: {
      title: "Dégâts",
      sessions: ["degats_caracterisation", "degats_precision_localisation"]
    },
    commentaires: {
      title: "Commentaires",
      sessions: ["commentaires"]
    },
    validation: {
      title: "Résumé /validation",
      sessions: ["validation"]
    }
  }
};
