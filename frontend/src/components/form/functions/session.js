import { formFunctions } from "@/components/form/functions/form.js";

const sessionFunctions = {


  /**
   * Vérifie la validité des formulaires pour chaque session définie dans la configuration.
   *
   * Parcourt tous les groupes de sessions dans la configuration, puis pour chaque session,
   * évalue la validité de tous les formulaires associés à cette session. La validité d'une session
   * est vraie uniquement si tous ses formulaires sont valides. Retourne un objet contenant,
   * pour chaque clé de session, un booléen indiquant si la session est valide.
   *
   * @param {Object} params - Les paramètres nécessaires à la validation.
   * @param {Object} params.$store - Le store Vuex ou l'état global de l'application.
   * @param {Object} params.baseModel - Le modèle de base utilisé pour la validation des formulaires.
   * @param {Object} params.config - La configuration contenant les définitions de sessions et de formulaires.
   * @returns {Object} Un objet dont les clés sont les identifiants de session et les valeurs sont des booléens indiquant la validité de chaque session.
   */
  validForms({ $store, baseModel, config }) {
    const validForms = {};
    for (const configSessionGroups of Object.values(config.sessionGroups)) {
      for (const sessionKey of configSessionGroups.sessions) {
        let validSession = true;
        const sessionDef = config.sessionDefs[sessionKey];
        for (const form of sessionFunctions.formList(sessionDef)) {
          validSession =
            validSession && formFunctions.isValidForm({ $store, baseModel, config }, form);
        }
        validForms[sessionKey] = validSession;
      }
    }
    return validForms;
  },


  /**
   * Renvoie la liste des formulaires associés à une configuration de session.
   *
   * Cette fonction permet d'obtenir la liste des formulaires à partir d'une configuration.
   * - Si la configuration possède une propriété 'groups', elle parcourt chaque groupe et agrège
   *   récursivement les formulaires de chaque groupe.
   * - Si la configuration possède une propriété 'forms', elle retourne directement cette liste.
   * - Sinon, elle retourne la liste des clés définies dans 'formDefs', correspondant aux identifiants des formulaires.
   *
   * @param {Object} config - La configuration de session ou de groupe de sessions.
   * @returns {Array} Un tableau contenant les identifiants des formulaires.
   */
  formList(config) {
    if (config.groups) {
      // Si la configuration contient des groupes, on agrège les formulaires de chaque groupe
      let list = [];
      for (const group of config.groups) {
        list = [...list, ...sessionFunctions.formList(group)];
      }
      return list;
    }
    if (config.forms) {
      // Si la configuration contient directement une liste de formulaires, on la retourne
      return config.forms;
    }
    // Sinon, on retourne les clés des définitions de formulaires
    return Object.keys(config.formDefs);
  },



  /**
   * Génère une liste de toutes les sessions à partir de la configuration fournie.
   *
   * Parcourt chaque groupe de sessions dans l'objet de configuration et extrait
   * toutes les clés de session pour les ajouter à une liste unique.
   *
   * @param {Object} config - La configuration contenant les groupes de sessions.
   * @param {Object} config.sessionGroups - Un objet où chaque propriété représente un groupe de sessions.
   * @returns {Array} sessionList - Un tableau contenant toutes les clés de session extraites des groupes.
   */
  sessionList(config) {
    const sessionList = [];
    for (const configSessionGroups of Object.values(config.sessionGroups)) {
      for (const keySession of configSessionGroups.sessions) {
        sessionList.push(keySession);
      }
    }

    return sessionList;
  },



  /**
   * Retourne la dernière session à partir de la liste des sessions générée par la fonction sessionList.
   *
   * @param {Object} config - La configuration utilisée pour générer la liste des sessions.
   * @returns {Object|undefined} La dernière session de la liste, ou undefined si la liste est vide.
   */
  lastSession(config) {
    const sessionList = sessionFunctions.sessionList(config);
    return sessionList[sessionList.length -1];
  },


  /**
   * Retourne la première session d'un groupe de sessions spécifique ou, si aucun groupe n'est spécifié,
   * la première session de la liste globale des sessions.
   *
   * @param {Object} config - L'objet de configuration contenant les groupes de sessions et la liste des sessions.
   * @param {string} [keySessionGroup] - La clé identifiant le groupe de sessions dont on souhaite obtenir la première session.
   * @returns {Object} La première session du groupe spécifié ou la première session globale si aucun groupe n'est fourni.
   */
  firstSession(config, keySessionGroup) {
    if (! keySessionGroup) {
      return sessionFunctions.sessionList(config)[0];
    }
    return config.sessionGroups[keySessionGroup].sessions[0]; 
  },


  /**
   * Retourne la session suivante dans la liste des sessions, basée sur la clé de session actuelle.
   *
   * @param {Object} config - La configuration utilisée pour générer la liste des sessions.
   * @param {string} keySession - La clé de la session courante pour laquelle on souhaite obtenir la suivante.
   * @returns {string|undefined} La clé de la session suivante si elle existe, sinon `undefined`.
   *
   * @description
   * Cette fonction recherche la position de la session courante dans la liste des sessions.
   * Si la session courante n'est pas trouvée ou si elle est la dernière de la liste, la fonction retourne `undefined`.
   * Sinon, elle retourne la clé de la session suivante dans la liste.
   */
  nextSession(config, keySession) {
    const sessionList = sessionFunctions.sessionList(config);
    const index = sessionList.indexOf(keySession);

    if (index === -1) {
      return;
    }

    if (index === sessionList.length - 1) {
      return;
    }

    return sessionList[index + 1];
  },


  /**
   * Retourne la liste des sessions associées à un groupe de session spécifique dans la configuration.
   *
   * @param {Object} config - L'objet de configuration contenant les groupes et leurs sessions.
   * @param {string} keySessionGroup - La clé identifiant le groupe de session dont on souhaite obtenir les sessions.
   * @returns {Array} La liste des sessions du groupe spécifié.
   */
  sessions(config, keySessionGroup) {
    return config.groups[keySessionGroup].sessions;
  },


  /**
   * Retourne la clé du groupe de session dont fait partie la session spécifiée.
   *
   * @param {Object} config - L'objet de configuration contenant les groupes de sessions.
   * @param {string} keySession - La clé de la session dont on souhaite connaître le groupe.
   * @returns {string|undefined} La clé du groupe de session si elle existe, sinon `undefined`.
   */
  group(config, keySession) {
    for (const [keySessionGroup, configSessionGroups] of Object.entries(
      config.sessionGroups
    )) {
      if (configSessionGroups.sessions.includes(keySession)) {
        return keySessionGroup;
      }
    }
    return;
  },

  /**
   * Retourne tous les groupes de sessions définis dans la configuration.
   *
   * @param {Object} config - L'objet de configuration contenant les groupes de sessions.
   * @returns {Array} La liste des groupes de sessions.
   */
  groups(config) {
    const groups = [];
    for (const configSessionGroups of Object.values(config.sessionGroups)) {
      const subGroups = []
      for (const keySession of configSessionGroups.sessions) {
        const sessionDef = config.sessionDefs[keySession];
        if (sessionDef) {
          subGroups.push(sessionDef);
        }
      }
      groups.push({
        groups: subGroups,
        title: configSessionGroups.title,
      })
    }
    return groups;
  },


  /**
   * Vérifie la validité d'une session spécifique en fonction de la configuration et des formulaires valides.
   *
   * @param {Object} params - Les paramètres nécessaires à la validation.
   * @param {Object} params.config - La configuration contenant les groupes de sessions.
   * @param {Object} params.baseModel - Le modèle de base utilisé pour la validation.
   * @param {Object} params.$store - Le store Vuex pour accéder aux états de l'application.
   * @param {string} keySessionTest - La clé de la session à tester pour la validité.
   * @returns {boolean} Retourne true si la session testée est valide selon les formulaires, sinon false.
   *
   * Cette fonction parcourt tous les groupes de sessions définis dans la configuration.
   * Pour chaque session, elle vérifie si la clé correspond à celle testée.
   * Si c'est le cas, elle retourne la condition de validité courante.
   * Sinon, elle met à jour la condition en fonction de la validité du formulaire associé à la session.
   */
  condValidSession({config, baseModel, $store}, keySessionTest) {
    const validForms = sessionFunctions.validForms({$store, baseModel, config})
    let cond = true;
    for (const configSessionGroups of Object.values(config.sessionGroups)) {
      for (const keySession of configSessionGroups.sessions) {
        if (keySessionTest == keySession) {
          return cond;
        }
        cond = cond && validForms[keySession];
      }
    }
  }


};

export { sessionFunctions }
