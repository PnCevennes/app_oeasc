<template>
  <div v-show="!configForm.hidden" :ref="config.name" class='dynamic-form'>
    <template v-if="configForm.displayValue && configForm.displayLabel">
      <b>{{ configForm.label }} : </b>
    </template>

    <!-- test config -->
    <template v-if="!configForm.valid">
      <label>{{ configForm.label }}</label>
      Problème avec la config
      {{ config }}
    </template>

    <!-- test cond-->
    <template v-else-if="!configForm.condition"> </template>

    <!-- list -->
    <template v-else-if="configForm.type === 'list'">
      <list :config="configForm" :baseModel="baseModel"></list>
    </template>

    <!-- Boolean radio -->
    <template v-else-if="configForm.type === 'bool_radio'">
      <span v-if="configForm.displayValue">
        <template v-if="baseModel[configForm.name] === true">{{
          configForm.labels[0]
        }}</template>
        <template v-else-if="baseModel[configForm.name] === false">{{
          configForm.labels[1]
        }}</template>
        <template v-else>Indéfini</template>
      </span>
      <v-radio-group
        v-else
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        row
        :rules="configForm.rules"
        @change="
          configForm.change && configForm.change({ baseModel, config, $store })
        "
      >
        <span v-if="config.required" class="required"> * </span>
        <help :code="`form-${config.name}`" v-if="config.help"></help>

        <v-radio :label="configForm.labels[0]" :value="true"></v-radio>
        <v-radio :label="configForm.labels[1]" :value="false"></v-radio>
      </v-radio-group>
    </template>

    <!-- Bolean switch -->
    <template v-else-if="configForm.type === 'bool_switch'">
      <span v-if="configForm.displayValue">
        <template v-if="baseModel[configForm.name] === true">Oui</template>
        <template v-else-if="baseModel[configForm.name] === false"
          >non</template
        >
        <template v-else>Indéfini</template>
      </span>
      <v-switch
        v-else
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        @change="
          configForm.change && configForm.change({ baseModel, config, $store })
        "
      ></v-switch>
    </template>

    <!-- text -->
    <template
      v-else-if="
        ['text', 'number', 'password', 'date'].includes(configForm.type)
      "
    >
      <span v-if="configForm.displayValue">
        {{ baseModel[configForm.name] }}
      </span>
      <v-text-field
        v-else
        :type="
          !show1 && config.type === 'password'
            ? 'password'
            : configForm.type == 'date'
            ? configForm.type
            : 'text'
        "
        :append-icon="
          config.type === 'password'
            ? show1
              ? 'mdi-eye'
              : 'mdi-eye-off'
            : null
        "
        dense
        v-model="baseModel[configForm.name]"
        :rules="configForm.rules"
        :label="configForm.label"
        :counter="configForm.counter"
        :maxlength="configForm.maxlength"
        :disabled="configForm.disabled"
        @change="
          configForm.change && configForm.change({ baseModel, config, $store })
        "
        @click:append="
          if (config.type === 'password') {
            show1 = !show1;
          }
        "
      >
        <span slot="label"
          >{{ config.label }}
          <span v-if="config.required && config.label" class="required">*</span>
        </span>
        {{ `form-${config.name}` }}

        <help
          slot="append"
          :code="`form-${config.name}`"
          v-if="config.help"
        ></help>
      </v-text-field>
    </template>

    <!-- text area -->
    <template v-else-if="configForm.type === 'text_area'">
      <span v-if="configForm.displayValue">
        {{ baseModel[configForm.name] }}
      </span>
      <v-textarea
        v-else
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        :placeholder="config.placeholder"
        outlined
      >
        <help
          slot="append"
          :code="`form-${config.name}`"
          v-if="config.help"
        ></help>
      </v-textarea>
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
      <list-form
        :config="configForm"
        :baseModel="baseModel"
        :dataItemsIn="config.items"
      ></list-form>
    </template>

    <!-- degats -->
    <template v-else-if="configForm.type === 'degats'">
      <degats-form :config="configForm" :baseModel="baseModel"></degats-form>
    </template>

    <!-- content -->
    <template v-else-if="configForm.type === 'content'">
      <oeasc-content
        :meta="configForm.meta"
        :code="configForm.code"
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
import list from "./list";

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
    help,
    list
  },

  data: () => ({
    show1: false,
    configTypes: [
      "input",
      "bool_radio",
      "bool_switch",
      "text",
      "date",
      "text_area",
      "nomenclature",
      "number",
      "select_map",
      "essence",
      "list_form",
      "degats",
      "content",
      "password",
      "list"
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
    },
    config: {
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
