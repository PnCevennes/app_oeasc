import { copy } from "@/core/js/util/util.js";
import { formFunctions } from "@/components/form/functions/form";

export default class ConfigDeclaration {
  _forms;
  _config;
  _sessions;

  constructor(config, sessions, forms) {
    this._config = config;
    this._sessions = sessions;
    this._forms = forms;
    this.initConfig(this._config);
  }

  initModel(model) {
    // const model = {};
    for (const [keyForm, form] of Object.entries(this._forms)) {
      model[keyForm] =
        model[keyForm] !== undefined
          ? model[keyForm]
          : form.multiple
          ? []
          : null;
      if (form.containerName) {
        model[form.containerName] =
          model[form.containerName] !== undefined
            ? model[form.containerName]
            : form.containerMultiple
            ? []
            : null;
      }
    }

    return model;
  }

  initValidForms({ $store, baseModel }, validForms) {
    {
      $store, baseModel;
    }
    validForms;
    for (const configSessionGroups of Object.values(this._config.groups)) {
      for (const session of Object.values(configSessionGroups.sessions)) {
        let validSession = true;
        for (const form of this.sessionFormList(session)) {
          validSession =
            validSession && this.isValidForm({ $store, baseModel }, form);
        }
        validForms[session.name] = validSession;
      }
    }
  }

  // liste des formulaires d'une session
  sessionFormList(session) {
    return this.groupFormList(session);
  }

  // liste des formulaires d'un groupe
  groupFormList(config) {
    if (config.groups) {
      let list = [];
      for (const group of Object.values(config.groups)) {
        list = [...list, ...this.groupFormList(group)];
      }
      return list;
    }
    return config.forms;
  }

  isValidForm({ $store, baseModel }, keyForm) {
    const form = copy(this._forms[keyForm]);

    let condRules = true;

    form.required =
      typeof this._forms[keyForm].required === "function"
        ? this._forms[keyForm].required({ $store, baseModel })
        : this._forms[keyForm].required;

    formFunctions.rules.processRules(form);

    for (const rule of form.rules) {
      condRules = condRules && rule(baseModel[keyForm]) === true;
    }

    let condCondition =
      !this._forms[keyForm].condition || this._forms[keyForm].condition({ baseModel, $store });

    return condRules || !condCondition;
  }

  initConfig(config) {
    const { groups, forms, sessions } = config;

    if (groups) {
      for (const configGroup of Object.values(groups)) {
        this.initConfig(configGroup);
      }
    }

    if (sessions) {
      const sessionList = copy(sessions);
      config.sessions = {};
      for (const sessionKey of sessionList) {
        const configSession = (config.sessions[sessionKey] = {
          ...this._sessions[sessionKey],
          name: sessionKey
        });
        this.initConfig(configSession);
      }
    }

    if (forms) {
      const formList = copy(forms);
      config.forms = {};
      for (const formKey of formList) {
        config.forms[formKey] = { ...this._forms[formKey], name: formKey };
      }
    }
  }

  config() {
    return this._config;
  }

  sessionList() {
    const sessionList = [];
    for (const configSessionGroups of Object.values(this._config.groups)) {
      for (const keySession of Object.keys(configSessionGroups.sessions)) {
        sessionList.push(keySession);
      }
    }

    return sessionList;
  }

  nextSession(keySession) {
    const sessionList = this.sessionList();
    const index = sessionList.indexOf(keySession);

    if (index === -1) {
      return;
    }

    if (index === sessionList.length - 1) {
      return;
    }

    return sessionList[index + 1];
  }

  sessions(keySessionGroup) {
    return this._config.groups[keySessionGroup].sessions;
  }

  firstSession(config, keySessionGroup) {
    return Object.keys(this._config.groups[keySessionGroup].sessions)[0];
  }

  group(keySession) {
    for (const [keySessionGroup, configSessionGroups] of Object.entries(
      this._config.groups
    )) {
      if (keySession in configSessionGroups.sessions) {
        return keySessionGroup;
      }
    }
    return;
  }

  condValidSession(keySessionTest, validForms) {
    let cond = true;
    for (const configSessionGroups of Object.values(this._config.groups)) {
      for (const keySession of Object.keys(configSessionGroups.sessions)) {
        if (keySessionTest == keySession) {
          return cond;
        }
        cond = cond && validForms[keySession];
      }
    }
  }
}
