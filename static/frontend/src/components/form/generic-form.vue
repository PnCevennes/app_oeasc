<template>
  <div v-if="config" class="form-container">
    {{baseModel}}
    <h2 v-if="title">{{ title }}</h2>
    <div v-if="bRequestSuccess">
      <slot name="success"></slot>
    </div>
    <div v-else>
      <slot name="prependForm"></slot>
      <v-form v-model="bValidForm" ref="form" v-if="bInit">
        <div>
          <dynamic-form-group
            :config="configDynamicGroupForm"
            :baseModel="baseModel"
          ></dynamic-form-group>
          <div>
            <span style="color:red">*</span>
            <i>champs obligatoires.</i>
          </div>
        </div>
        <template v-if="!displayValue">
          <v-btn
            v-if="config.action"
            absolute
            right
            color="success"
            @click="processAction()"
            :disabled="bSending || baseModel.freeze"
            >{{ config.action.label || "Valider" }}</v-btn
          >
        </template>
        <v-btn
          v-if="switchDisplay"
          color="primary"
          @click="processAnnulerModifier()"
          >{{ displayValue ? "Modifier" : "Annuler" }}</v-btn
        >

        <v-btn
          v-if="config.cancel"
          color="primary"
          @click="config.cancel.action({ baseModel })"
          >Annuler</v-btn
        >

        <v-progress-linear
          indeterminate
          color="green"
          v-if="bSending"
        ></v-progress-linear>

        <slot name="appendForm"></slot>
      </v-form>
    </div>
    <v-snackbar color="error" v-model="bError" :timeout="5000">
      {{ msgError }}
    </v-snackbar>
    <v-snackbar color="success" v-model="bSuccess" :timeout="2000">
      {{ msgSuccess }}
    </v-snackbar>
  </div>
</template>

<script>
import { apiRequest } from "@/core/js/data/api.js";
import dynamicFormGroup from "@/components/form/dynamic-form-group";
import { config as globalConfig } from "@/config/config.js";
import { copy } from "@/core/js/util/util";

// import {copy} from '@/core/js/util/util'

export default {
  name: "generic-form",
  components: {
    dynamicFormGroup
  },
  props: ["config"],
  computed: {
    idRoute() {
      return this.$route.params.id;
    },
    idModel() {
      return (
        (this.baseModel && this.baseModel[this.config.idFieldName]) ||
        (this.config.value && this.config.value[this.config.idFieldName])
      );
    },
    configDynamicGroupForm() {
      return {
        groups: this.config.groups,
        forms: this.config.forms,
        formDefs: this.config.formDefs,
        displayValue: this.displayValue,
        displayLabel: this.config.displayLabel
      };
    },
    method() {
      return typeof this.config.action.request.method === "function"
        ? this.config.action.request.method({ id: this.idModel })
        : this.config.action.request.method;
    },
    url() {
      return typeof this.config.action.request.url === "function"
        ? this.config.action.request.url({ id: this.idModel })
        : this.config.action.request.url;
    },
    switchDisplay() {
      return typeof this.config.switchDisplay == "function"
        ? this.config.switchDisplay({ id: this.idModel })
        : this.config.switchDisplay;
    },
    title() {
      return typeof this.config.title == "function"
        ? this.config.title({ id: this.idModel })
        : this.config.title;
    }
  },
  watch: {
    config() {
      this.initConfig();
    },
    idRoute() {
      this.baseModel[this.config.idFieldName] = this.idRoute;
      this.initConfig();
    }
  },
  mounted() {
    this.initConfig();
  },
  methods: {
    processAnnulerModifier() {
      setTimeout(() => {
        if (!this.displayValue) {
          this.baseModel = copy(this.baseModelSave);
        }
        this.displayValue = !this.displayValue;
      }, 100);
    },
    initConfig() {
      this.displayValue =
        typeof this.config.displayValue == "function"
          ? this.config.displayValue({ id: this.idModel })
          : this.config.displayValue;
      if (!this.config) return;
      this.bInit = false;
      const storeName = this.config.storeName;
      if (storeName) {
        const configStore = this.$store.getters.configStore(storeName);

        // const storeNameCapitalized =
        //   storeName.charAt(0).toUpperCase() + storeName.slice(1);
        // const storeNameIdFieldName = `${storeName}IdFieldName`;
        // this.config.idFieldName = this.$store.getters[storeNameIdFieldName];
        this.config.preLoadData = ({ $store, id, config }) => {
          return new Promise(resolve => {
            if (!id) {
              resolve();
            } else {
              $store
                .dispatch(configStore.get, { id })
                .then(data => {
                  config.value = data;
                  this.baseModel = null;
                  resolve();
                });
            }
          });
        };
        this.config.action = this.config.action || {};
        this.config.action.process = ({ id, $store, postData }) => {
          return $store.dispatch(
            id ? configStore.patch : configStore.post,
            {
              id: id,
              postData
            }
          );
        };

        if (!this.config.action.onSuccess) {
          this.config.action.onSuccess = ({ $router, $store, data, id }) => {
            if (!id) {
              const id_ = data[$store.getters[`${storeName}idFieldName`]];
              $router.push(`${$router.history.current.path}${id_}`);
            }
          };
        }
      }

      if (this.config.preLoadData) {
        this.config
          .preLoadData({
            $store: this.$store,
            config: this.config,
            id: this.idModel
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
      baseModel = this.baseModel || this.config.value || {};
      for (const [keyForm, formDef] of Object.entries(this.config.formDefs)) {
        baseModel[keyForm] =
          baseModel[keyForm] != undefined
            ? baseModel[keyForm]
            : formDef.multiple
            ? []
            : null;
      }
      baseModel.freeze = false;
      this.baseModel = baseModel;
      this.baseModelSave = copy(this.baseModel);
    },
    postData() {
      return this.config.action.preProcess
        ? this.config.action.preProcess({
            baseModel: this.baseModel,
            globalConfig,
            config: this.config
          })
        : this.baseModel;
    },
    processAction() {
      setTimeout(() => {
        this.bValidForm = this.$refs.form.validate();
        if (!this.bValidForm) {
          return;
        }

        let promise = this.config.action.request
          ? this.request()
          : this.config.action.process &&
            this.config.action.process({
              postData: this.postData(),
              $store: this.$store,
              $router: this.$router,
              config: this.config,
              id: this.idModel
            });

        if (!promise) return;

        this.bSending = true;

        promise.then(
          data => {
            this.bSending = false;

            if (!this.config.bChained) {
              this.bSuccess = true;
              this.msgSuccess = "La requête à été effectuée avec succès";
            }

            if (this.config.action.onSuccess) {
              this.config.action.onSuccess({
                data,
                $session: this.$session,
                $store: this.$store,
                $router: this.$router,
                $route: this.$route,
                id: this.idModel
              });
            }
            if (this.switchDisplay) {
              this.displayValue = true;
            } else if(!this.config.bChained){
              this.bRequestSuccess = true;
            }
          },
          error => {
            this.bSending = false;
            this.bError = true;
            this.msgError = `Erreur avec la requête : ${error.msg}`;
          }
        );
      }, 100);
    },

    request() {
      return apiRequest(this.method, this.url, {
        postData: this.postData()
      });
    }
  },
  data: () => ({
    bValidForm: null,
    bInit: false,
    baseModel: null,
    baseModelSave: null,
    msgError: null,
    bError: false,
    msgSuccess: null,
    bSuccess: false,
    bRequestSuccess: false,
    bSending: false,
    recompConfig: true,
    displayValue: null
  })
};
</script>

<style>
.form-container {
  min-width: 800px;
  position: relative;
}
</style>
