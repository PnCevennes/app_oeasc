<template>
  <div v-if="configForm" class="form-container">
    <div v-if="bRequestSuccess" class="red">
      <slot name="success"></slot>
    </div>
    <div v-else>
      <slot name="prependForm"></slot>

      <v-form v-model="bValidForm" ref="form" v-if="bInit">
        <div v-if="config.display == 'table'">
          <v-simple-table>
            <template
              v-for="[key, form] in Object.entries(configForm.forms || {})"
            >
              <tr
                :key="key"
                v-if="form.condition === undefined || form.condition"
              >
                <th>
                  {{ form.label }}
                  <span v-if="form.required" class="required">*</span>
                </th>
                <td>
                  <dynamic-form
                    :config="{
                      ...form,
                      ...{
                        name: key,
                        label: '',
                        dense: true,
                        displayValue: configForm.displayValue
                      }
                    }"
                    :baseModel="baseModel"
                  ></dynamic-form>
                </td>
              </tr>
            </template>
          </v-simple-table>
        </div>
        <div v-else>
          <dynamic-form-group
            :config="{ ...configForm, displayValue: config.displayValue }"
            :baseModel="baseModel"
          >
          </dynamic-form-group>
        </div>

        <template v-if="!config.displayValue">
          <v-btn
            v-if="configForm.request"
            absolute
            right
            color="success"
            @click="submit()"
            :disabled="bSending"
          >
            {{ configForm.request.label || "Valider" }}
          </v-btn>
        </template>
        <v-btn
          v-if="configForm.switchDisplay"
          color="primary"
          @click="
            config.displayValue = !config.displayValue;
            recompConfig = !recompConfig;
          "
        >
            <!-- config = { ...config }; -->
          {{ configForm.displayValue ? "Modifier" : "Annuler" }}
        </v-btn>

        <v-btn
          v-if="configForm.cancel"
          color="primary"
          @click="configForm.cancel.action({ baseModel })"
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
import dynamicForm from "@/components/form/dynamic-form";
import dynamicFormGroup from "@/components/form/dynamic-form-group";

export default {
  name: "generic-form",
  components: { dynamicForm, dynamicFormGroup },
  props: ["config"],
  computed: {
    configForm() {
      this.recompConfig;
      return this.initConfig(this.config, this.baseModel);
    }
  },
  methods: {
    initConfig(config, baseModel) {
      const configNew = {};
      for (const [key, subConfig] of Object.entries(config)) {
        if (
          typeof subConfig === "object" &&
          subConfig &&
          !Array.isArray(subConfig)
        ) {
          configNew[key] = this.initConfig(subConfig, baseModel);
        } else if (
          typeof subConfig == "function" &&
          ["required", "condition", "disabled", "items"].includes(key)
        ) {
          configNew[key] = subConfig({
            baseModel: baseModel,
            $store: this.$store
          });
        } else {
          configNew[key] = config[key];
        }
      }
      if (this.config.value) {
        this.baseModel = this.config.value || this.baseModel;
      }
      return configNew;
    },
    submit() {
      let postData = this.config.request.preProcess
        ? this.config.request.preProcess({ baseModel: this.baseModel })
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
            this.config.request.onSuccess(data);
          }
          if (this.config.switchDisplay) {
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
    // configForm: {},
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
