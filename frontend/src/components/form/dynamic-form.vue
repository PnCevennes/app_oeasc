<template>
  <div v-show="!configForm.hidden" :ref="config.name" class="dynamic-form">

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
    <template v-else-if="!configForm.condition"></template>

    <!-- list -->
    <template v-else-if="configForm.type === 'list'">
      <list :config="configForm" :baseModel="baseModel"></list>
    </template>

    <!-- Boolean radio -->
    <template v-else-if="configForm.type === 'bool_radio'">
      <span v-if="configForm.displayValue">
        <template v-if="baseModel[configForm.name] === true">
          {{ configForm.labels[0] }}
        </template>
        <template v-else-if="baseModel[configForm.name] === false">
          {{ configForm.labels[1] }}
        </template>
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
        <span v-if="config.required" class="required">*</span>
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
        :id="`form-${config.name}`"
        v-else
        dense
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        :disabled="configForm.disabled"
        @change="
          configForm.change && configForm.change({ baseModel, config, $store })
        "
      ></v-switch>
    </template>

    <!-- text -->
    <template
      v-else-if="
        ['text', 'number', 'password', 'date', 'email'].includes(
          configForm.type
        )
      "
    >
      <span v-if="configForm.displayValue">{{
        baseModel[configForm.name]
      }}</span>
      <v-text-field
        v-else
        :id="`form-${configForm.name}`"
        :type="
          !show1 && configForm.type === 'password'
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
        @change="inputChange($event)"
      >
        <span slot="label">
          {{ configForm.label }}
          <span v-if="configForm.required && config.label" class="required"
            >*</span
          >
        </span>
        {{ `form-${config.name}` }}

        <span slot="append" @click="show1 = !!show1">
          <v-btn
            icon
            v-if="config.type === 'password'"
            @click="show1 = !show1"
            tabindex="-1"
          >
            <v-icon>
              {{
                config.type === "password"
                  ? show1
                    ? "mdi-eye"
                    : "mdi-eye-off"
                  : null
              }}
            </v-icon>
          </v-btn>
          <help
            tabindex="-1"
            :code="`form-${configForm.name}`"
            v-if="configForm.help"
          ></help>
        </span>
      </v-text-field>
    </template>

    <!-- text area -->
    <template v-else-if="configForm.type === 'text_area'">
      <span v-if="configForm.displayValue">{{
        baseModel[configForm.name]
      }}</span>
      <v-textarea
        v-else
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        :placeholder="configForm.placeholder"
        :rows="configForm.rows"
      >
        <help
          slot="append"
          :code="`form-${configForm.name}`"
          v-if="configForm.help"
        ></help>
      </v-textarea>
    </template>

    <template v-else-if="configForm.type === 'file'">
      <span v-if="configForm.displayValue">{{
        baseModel[configForm.name]
      }}</span>
      <v-file-input
        v-else
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        :placeholder="configForm.placeholder"
      >
        <help
          slot="append"
          :code="`form-${configForm.name}`"
          v-if="configForm.help"
        ></help>
      </v-file-input>
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
        :meta="configForm.meta"
        :code="configForm.code"
        :containerClassIn="'content-container-form'"
      ></oeasc-content>
    </template>
    <template v-else-if="configForm.type === 'button'">
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn
            v-on="on"
            :icon="!!configForm.icon"
            @click="configForm.click({ baseModel })"
          >
            {{ configForm.label }}
            <v-icon v-if="configForm.icon">{{ configForm.icon }}</v-icon>
          </v-btn>
        </template>
        <span>{{ configForm.tooltip }}</span>
      </v-tooltip>
    </template>
  </div>
</template>

<script>
import nomenclatureForm from "./nomenclature-form";
import listForm from "./list-form";
import selectMap from "./select-map.vue";
import essenceForm from "./essence-form.vue";
import degatsForm from "./degats-form.vue";
import help from "./help";
import list from "./list";
import { copy } from "@/core/js/util/util";

import { formFunctions } from "@/components/form/functions/form";

export default {
  name: "dynamicForm",

  components: {
    nomenclatureForm,
    selectMap,
    essenceForm,
    listForm,
    degatsForm,
    oeascContent: () => import("@/modules/content/content.vue"),
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
      "email",
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
      "list",
      "button",
      "file"
    ],
    configForm: null
  }),

  props: ["config", "baseModel"],

  // bidouille à voir si on y arrive avec computed
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
    inputChange(event) {
      event;
      // si on a '' pour number => erreur insert sql
      if(this.configForm.type == 'number' && this.baseModel[this.config.name] == '') {
        this.baseModel[this.config.name]=null
      }
      return this.configForm.change && this.configForm.change({ baseModel: this.baseModel, config : this.config, $store: this.$store })
    },

    getConfigForm: function() {
      const configResolved = { condition: true, valid: true };

      // if(this.config.multiple && !this.baseModel[this.config.name]) {
      //   this.baseModel[this.config.name] = this.baseModel[this.config.name]||[];
      // }

      if (this.config && this.config.storeName) {
        const configStore = this.$store.getters.configStore(
          this.config.storeName
        );

        // defaults
        this.config.idFieldName =
          this.config.idFieldName || configStore.idFieldName;
        this.config.displayFieldName =
          this.config.displayFieldName || configStore.displayFieldName;
        this.config.api = this.config.api || configStore.apis;

        // select
        // this.config.type = this.config.type || configStore.type || "list_form";
        // this.config.list_type =
        //   this.config.list_type || configStore.list_type || "select";

        // si autocomplete => serverSide ??
        // if (["autocomplete", "combobox"].includes(this.config.list_type)) {
        //   this.config.dataReloadOnSearch = true;
        //   this.config.params = {
        //     sortBy: [this.config.displayFieldName],
        //     sortDesc: [false],
        //     itemsPerPage: 10,
        //     ...(this.config.params || {})
        //   };
        // }
        // this.config.returnObject = [null, undefined].includes(
        //     this.config.returnObject
        //   )
        //     ? true
        //     : this.config.returnObject;
        // on passe en parametre
        // this.config.url = ({ search, config }) => {
        //   const url = `${config.api}?${config.displayFieldName}__ilike=${search}`;
        //   return url;
        // };
      }

      for (const key in this.config) {
        if (
          typeof this.config[key] === "function" &&
          !["change", "processItems", "url"].includes(key) //TODO à voir pour URL
        ) {
          // on resout les fonctions
          configResolved[key] = this.config[key]({
            baseModel: this.baseModel,
            $store: this.$store
          });
        } else {
          configResolved[key] = copy(this.config[key]);
        }
      }

      // configResolved.rules = (this.configResolved.rules || []).map(r => r);

      //teste si type dans type autorisé
      configResolved.valid = this.configTypes.includes(this.config.type);

      // ajout automatique de regle selon le type
      formFunctions.rules.processRules(configResolved);

      // si default et non attribué => on lui donne la valeur
      if (configResolved.default && !this.baseModel[this.config.name]) {
        // si promise ou non ??
        Promise.resolve(configResolved.default).then(value => {
          this.baseModel[this.config.name] = value;
        });
      }

      return configResolved;
    }
  },

  created: function() {
    this.configForm = this.getConfigForm();
  }
};
</script>

<style scoped>
@import url("./form.css");
</style>
