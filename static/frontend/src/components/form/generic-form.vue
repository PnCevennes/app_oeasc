<template>
  <div v-if="config" class="form-container">
    <h2 v-if="title">{{title}}</h2>
    <div v-if="bRequestSuccess">
      <slot name="success"></slot>
    </div>
    <div v-else>
      <slot name="prependForm"></slot>

      <v-form v-model="bValidForm" ref="form" v-if="bInit">
        <div>
          <dynamic-form-group :config="configDynamicGroupForm" :baseModel="baseModel"></dynamic-form-group>
        </div>

        <template v-if="!config.displayValue">
          <!-- pour les requetes -->
          <v-btn
            v-if="config.request"
            absolute
            right
            color="success"
            @click="submit()"
            :disabled="bSending"
          >{{ config.request.label || "Valider" }}</v-btn>
          <!-- pour les actions (par exemple aller au formulaire suivant) -->
          <v-btn
            v-if="config.action"
            absolute
            right
            color="success"
            @click="processAction()"
            :disabled="bSending"
          >{{ config.action.label || "Valider" }}</v-btn>
        </template>
        <v-btn
          v-if="switchDisplay"
          color="primary"
          @click="
            config.displayValue = !config.displayValue;
            recompConfig = !recompConfig;
          "
        >{{ config.displayValue ? "Modifier" : "Annuler" }}</v-btn>

        <v-btn
          v-if="config.cancel"
          color="primary"
          @click="config.cancel.action({ baseModel })"
        >Annuler</v-btn>

        <v-progress-linear indeterminate color="green" v-if="bSending"></v-progress-linear>

        <slot name="appendForm"></slot>
      </v-form>
    </div>
    <v-snackbar color="error" v-model="bError" :timeout="5000">
      {{
      msgError
      }}
    </v-snackbar>
    <v-snackbar color="success" v-model="bSuccess" :timeout="2000">
      {{
      msgSuccess
      }}
    </v-snackbar>
  </div>
</template>

<script>
import { apiRequest } from "@/core/js/data/api.js";
import dynamicFormGroup from "@/components/form/dynamic-form-group";
import { config as globalConfig } from "@/config/config.js";
// import {copy} from '@/core/js/util/util'

export default {
  name: "generic-form",
  components: {
    dynamicFormGroup
  },
  props: ["config", "meta"],
  computed: {
    configDynamicGroupForm() {
      return {
        groups: this.config.groups,
        forms: this.config.forms,
        formDefs: this.config.formDefs,
        displayValue: this.config.displayValue,
        displayLabel: this.config.displayLabel
      };
    },
    method() {
      return typeof this.config.request.method === "function"
        ? this.config.request.method({ meta: this.meta })
        : this.config.request.method;
    },
    url() {
      return typeof this.config.request.url === "function"
        ? this.config.request.url({ meta: this.meta })
        : this.config.request.url;
    },
    switchDisplay() {
      return typeof this.config.switchDisplay == "function"
        ? this.config.switchDisplay({ meta: this.meta })
        : this.config.switchDisplay;
    },
    title() {
      return typeof this.config.title == "function"
        ? this.config.title({ meta: this.meta })
        : this.config.title;
    }
  },
  watch: {
    config() {
      this.initConfig();
    }
  },
  mounted() {
    this.initConfig();
  },
  methods: {
    processAction() {
      if (!this.$refs.form.validate()) return;
      this.config &&
        this.config.action.process &&
        this.config.action.process(this);
    },
    initConfig() {
      if (!this.config) return;
      this.bInit = false;
      if (this.config.preLoadData) {
        this.config
          .preLoadData({
            $store: this.$store,
            config: this.config,
            meta: this.meta
          })
          .then(() => {
            this.initBaseModel();
            this.bInit = true;
          });
      } else {
        this.initBaseModel();
        this.bInit = true;
      }
    },
    initBaseModel() {
      let baseModel = {};
      baseModel = this.baseModel||this.config.value||{};
      for (const [keyForm, formDef] of Object.entries(this.config.formDefs)) {
        if (formDef.multiple && !baseModel[keyForm]) {
          baseModel[keyForm] = [];
        }
      }
      this.baseModel = baseModel;
    },
    submit() {
      let postData = this.config.request.preProcess
        ? this.config.request.preProcess({
            baseModel: this.baseModel,
            globalConfig,
            config: this.config
          })
        : this.baseModel;
      this.$refs.form.validate();
      if (!this.bValidForm) {
        return;
      }
      this.bSending = true;

      apiRequest(this.method, this.url, {
        data: postData
      }).then(
        data => {
          this.bSending = false;
          this.bSuccess = true;
          this.msgSuccess = "La requête à été effectuée avec succès";

          if (this.config.request.onSuccess) {
            this.config.request.onSuccess({
              data,
              $session: this.$session,
              $store: this.$store,
              $router: this.$router,
              redirect: this.redirect
            });
          }
          if (this.switchDisplay) {
            this.config.displayValue = true;
          } else {
            this.bRequestSuccess = true;
          }
        },
        error => {
          this.bSending = false;
          this.bError = true;
          this.msgError = `Erreur avec la requête : ${error.msg}`;
        }
      );
    }
  },
  data: () => ({
    bValidForm: null,
    bInit: false,
    baseModel: null,
    msgError: null,
    bError: false,
    msgSuccess: null,
    bSuccess: false,
    bRequestSuccess: false,
    bSending: false,
    recompConfig: true
  })
};
</script>


<style>
.form-container {
  min-width: 800px;
  position: relative;
}

</style>
