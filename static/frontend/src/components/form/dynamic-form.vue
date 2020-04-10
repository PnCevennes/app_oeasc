<template>
  <div v-show="!configForm.hidden">
    <!-- test config -->

    <!-- <i>
      {{ configForm.name }}
    </i>
    <b>
      {{ baseModel[configForm.name] }}
    </b> -->

    <template v-if="!configForm.valid">
      <label>{{ configForm.label }}</label>
      Problème avec la config
      {{ config }}
    </template>

    <!-- test cond-->
    <template v-else-if="!configForm.condition"> </template>

    <!-- input -->
    <!-- <template v-else-if="configForm.type === 'input'">
      <input v-model="baseModel[configForm.name]" />
    </template> -->

    <!-- Boolean radio -->
    <template v-else-if="configForm.type === 'bool_radio'">
      <v-radio-group
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        row
        :rules="configForm.rules"
        @change="
          configForm.change && configForm.change({ baseModel, config, $store })
        "
      >
        <help :code="`form-${config.name}`" v-if="config.help"></help>

        <v-radio :label="configForm.labels[0]" :value="true"></v-radio>
        <v-radio :label="configForm.labels[1]" :value="false"></v-radio>
      </v-radio-group>
    </template>

    <!-- Bolean switch -->
    <template v-else-if="configForm.type === 'bool_switch'">
      <v-switch
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
      ></v-switch>
    </template>

    <!-- text -->
    <template v-else-if="configForm.type === 'text'">
      <v-text-field
        v-model="baseModel[configForm.name]"
        :rules="configForm.rules"
        :label="configForm.label"
        :counter="configForm.counter"
        :maxlength="configForm.maxlength"
        :disabled="configForm.disabled"
        @change="configForm.change && configForm.change(baseModel)($event)"
      >
        <help
          slot="append"
          :code="`form-${config.name}`"
          v-if="config.help"
        ></help>
      </v-text-field>
    </template>

    <!-- text area -->
    <template v-else-if="configForm.type === 'text_area'">
      <v-textarea
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
      >
        <help
          slot="append"
          :code="`form-${config.name}`"
          v-if="config.help"
        ></help>
      </v-textarea>
    </template>

    <!-- number -->
    <template v-else-if="configForm.type === 'number'">
      <v-text-field
        v-model="baseModel[configForm.name]"
        :rules="configForm.rules"
        :label="configForm.label"
        :counter="configForm.counter"
        :maxlength="configForm.maxlength"
        :disabled="configForm.disabled"
        :placeholder="configForm.placeholder"
        type="number"
      >
        <help
          slot="append"
          :code="`form-${config.name}`"
          v-if="config.help"
        ></help>
      </v-text-field>
    </template>

    <!-- nomenclature -->
    <template v-else-if="configForm.type === 'nomenclature'">
      <nomenclature-form
        :config="configForm"
        :baseModel="baseModel"
      ></nomenclature-form>
    </template>

    <!-- essence -->
    <template v-else-if="configForm.type === 'essence'">
      <essence-form :config="configForm" :baseModel="baseModel"></essence-form>
    </template>

    <!-- select map -->
    <template v-else-if="configForm.type === 'select_map'">
      <select-map :config="configForm" :baseModel="baseModel"></select-map>
    </template>

    <!-- list form -->
    <template v-else-if="configForm.type === 'list_form'">
      <list-form :config="configForm" :baseModel="baseModel"></list-form>
    </template>

    <!-- degats -->
    <template v-else-if="configForm.type === 'degats'">
      <degats-form :config="configForm" :baseModel="baseModel"></degats-form>
    </template>

    <!-- content -->
    <template v-else-if="configForm.type === 'content'">
      <oeasc-content
        :code="config.code"
        :containerClassIn="'content-container-form'"
      ></oeasc-content>
    </template>
  </div>
</template>

<script>
import nomenclatureForm from "./nomenclature-form";
import listForm from "./list-form";
import selectMap from "./select-map.vue";
import essenceForm from "./essence-form.vue";
import degatsForm from "./degats-form.vue";
import oeascContent from "@/modules/content/content";
import help from "./help";

import { formFunctions } from "@/components/form/functions.js";

export default {
  name: "dynamicForm",

  components: {
    nomenclatureForm,
    selectMap,
    essenceForm,
    listForm,
    degatsForm,
    oeascContent,
    help
  },

  data: () => ({
    configTypes: [
      "input",
      "bool_radio",
      "bool_switch",
      "text",
      "text_area",
      "nomenclature",
      "number",
      "select_map",
      "essence",
      "list_form",
      "degats",
      "content"
    ],
    configForm: null
  }),

  props: ["config", "baseModel"],

  watch: {
    baseModel: {
      handler() {
        this.configForm = this.getConfigForm();
      },
      deep: true
    }
  },

  methods: {
    getConfigForm: function() {
      const configResolved = { condition: true, valid: true };

      for (const key in this.config) {
        if (
          typeof this.config[key] === "function" &&
          !["change", "processItems", "url"].includes(key)
        ) {
          configResolved[key] = this.config[key]({
            baseModel: this.baseModel,
            $store: this.$store
          });
        } else {
          configResolved[key] = this.config[key];
        }
      }

      configResolved.rules = (this.config.rules || []).map(r => r);

      configResolved.valid = this.configTypes.includes(this.config.type);
      formFunctions.rules.processRules(configResolved);

      return configResolved;
    }
  },

  created: function() {
    this.configForm = this.getConfigForm();
  }
};
</script>
