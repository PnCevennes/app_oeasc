import { copy } from "@/core/js/util/util.js";

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
        model[keyForm] != undefined
          ? model[keyForm]
          : form.multiple
          ? []
          : null;
      if (form.containerName) {
        model[form.containerName] =
          model[form.containerName] != undefined
            ? model[form.containerName]
            : form.containerMultiple
            ? []
            : null;
      }
    }

    return model;
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

  initValidForms() {
    const validForm = {};
    for (const key of Object.keys(this._sessions)) {
      validForm[key] = null;
    }
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

  firstSession(keySessionGroup) {
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
}
