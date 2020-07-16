<template>
  <div v-if="config" class="form-container">
    <div v-if="bRequestSuccess" class="red">
      <slot name="success"></slot>
    </div>
    <div v-else>
      <slot name="prependForm"></slot>

      <v-form v-model="bValidForm" ref="form" v-if="bInit">
        <div>
          <dynamic-form-group
            :config="configDynamicGroupForm"
            :baseModel="baseModel"
          >
          </dynamic-form-group>
        </div>

        <template v-if="!displayValue">
          <v-btn
            v-if="config.request"
            absolute
            right
            color="success"
            @click="submit()"
            :disabled="bSending"
          >
            {{ config.request.label || "Valider" }}
          </v-btn>
        </template>
        <v-btn
          v-if="config.switchDisplay"
          color="primary"
          @click="
            displayValue = !displayValue;
            recompConfig = !recompConfig;
          "
        >
          {{ displayValue ? "Modifier" : "Annuler" }}
        </v-btn>

        <v-btn
          v-if="config.cancel"
          color="primary"
          @click="config.cancel.action({ baseModel })"
        >
          Annuler
        </v-btn>

        <v-progress-linear
          indeterminate
          color="green"
          v-if="bSending"
        ></v-progress-linear>

        <slot name="appendForm"></slot>
      </v-form>
    </div>
    <v-snackbar color="error" v-model="bError" :timeout="5000">{{
      msgError
    }}</v-snackbar>
    <v-snackbar color="success" v-model="bSuccess" :timeout="2000">{{
      msgSuccess
    }}</v-snackbar>
  </div>
</template>

<script>
import { apiRequest } from "@/core/js/data/api.js";
// import dynamicForm from "@/components/form/dynamic-form";
import dynamicFormGroup from "@/components/form/dynamic-form-group";
import { config as globalConfig } from "@/config/config.js";

export default {
  name: "generic-form",
  components: {
    // dynamicForm,
    dynamicFormGroup
  },
  props: ["config"],
  computed: {
    configDynamicGroupForm() {
      return {
        struct: this.config.struct,
        forms: this.config.forms,
        displayValue: this.displayValue
      };
    }
  },
  methods: {
    submit() {
      let postData = this.config.request.preProcess
        ? this.config.request.preProcess({
            baseModel: this.baseModel,
            globalConfig
          })
        : this.baseModel;
      this.$refs.form.validate();
      if (!this.bValidForm) {
        return;
      }
      this.bSending = true;
      apiRequest(this.config.request.method, this.config.request.url, {
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
              redirect: this.redirect,
            });
          }
          if (this.config.switchDisplay) {
            this.displayValue = true;
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
    baseModel: {},
    msgError: null,
    bError: false,
    msgSuccess: null,
    bSuccess: false,
    bRequestSuccess: false,
    bSending: false,
    recompConfig: true,
    displayValue: false
  }),
  mounted() {
    if (this.config.preLoadData) {
      this.config
        .preLoadData({ $store: this.$store, config: this.config })
        .then(() => {
          this.baseModel = this.config.value || {};
          this.bInit = true;
        });
    } else {
      this.bInit = true;
    }
  }
};
</script>
