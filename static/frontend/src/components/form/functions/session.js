import { formFunctions } from "@/components/form/functions/form";

const sessionFunctions = {

  // renvoie un dictionnaire {key : form[key] valid)
  validForms({ $store, baseModel, config }) {
    const validForms = {};
    for (const configSessionGroups of Object.values(config.sessionGroups)) {
      for (const sessionKey of Object.values(configSessionGroups.sessions)) {
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


  // liste des formulaires d une config
  // soit de groupe
  // soit la liste forms
  // soit les clé de formDef
  formList(config) {
    if (config.groups) {
      let list = [];
      for (const group of config.groups) {
        list = [...list, ...sessionFunctions.groupFormList(group)];
      }
      return list;
    }
    if (config.forms) {
      return config.forms
    }
    return Object.keys(config.formDefs);
  },

  // Renvoie la liste des sessions de tous les groupes
  sessionList(config) {
    const sessionList = [];
    for (const configSessionGroups of Object.values(config.sessionGroups)) {
      for (const keySession of configSessionGroups.sessions) {
        sessionList.push(keySession);
      }
    }

    return sessionList;
  },

  // renvoie la dernière session
  lastSession(config) {
    const sessionList = sessionFunctions.sessionList(config);
    return sessionList[sessionList.length -1];
  },

  // renvoie la premiere session du groupe ou de tous si keySessionGroup n'est pas défini
  firstSession(config, keySessionGroup) {
    if (! keySessionGroup) {
      return sessionFunctions.sessionList(config)[0];
    }
    return config.sessionGroups[keySessionGroup].sessions[0]; 
  },

  // renvoie la session suivante
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

  // renvoie les session d'un groupe (clés)
  sessions(config, keySessionGroup) {
    return config.groups[keySessionGroup].sessions;
  },

  // renvoie la clé du groupe de session dont fait partie keySession
  group(config, keySession) {
    for (const [keySessionGroup, configSessionGroups] of Object.entries(
      config.sessionGroups
    )) {
      if (keySession in configSessionGroups.sessions) {
        return keySessionGroup;
      }
    }
    return;
  },

  // renvoie tous les groupes
  groups(config) {
    const groups = [];
    for (const configSessionGroups of Object.values(config.sessionGroups)) {
      for (const keySession of configSessionGroups.sessions) {
        const sessionDef = config.sessionDefs[keySession];
        if (sessionDef)
        groups.push(sessionDef.groups);
      }
    }
    return groups;
  },

  // renvoie si une session est valide
  condValidSession({config, validForms}, keySessionTest) {
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
