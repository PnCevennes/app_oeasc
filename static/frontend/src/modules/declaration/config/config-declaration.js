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

  initModel() {
    const model = {};
    for (const [keyForm, form] of Object.entries(this._forms)) {
      model[keyForm] = form.multiple ? [] : null;
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
        const configSession = config.sessions[sessionKey] = { ...this._sessions[sessionKey], name: sessionKey } ;
        this.initConfig(configSession)
      }
    }

    if (forms) {
      const formList = copy(forms);
      config.forms = {};
      for (const formKey of formList) {
        config.forms[formKey] = { ...this._forms[formKey], name: formKey};
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
}
