<template>
  <div>
    <b v-if="!config.displayValue">{{ config.label }}</b>
    <v-row dense>
      <v-col class="col-btn"></v-col>
      <v-col v-for="keyForm of config.forms.filter(keyForm => !config.formDefs[keyForm].hidden)" :key="keyForm">
        {{config.formDefs[keyForm].hidden}}
        <b v-if="!config.formDefs[keyForm].hidden">{{config.formDefs[keyForm].label}}</b>
      </v-col>
    </v-row>

    <v-row dense v-for="(lineModel, indexLine) of lines" :key="indexLine">
      <v-col class="col-btn">
        <v-btn icon color="red" @click="deleteItem(indexLine)" v-if="!config.displayValue">
          <v-icon>mdi-close-circle</v-icon>
        </v-btn>
      </v-col>

      <v-col v-for="keyForm of config.forms.filter(keyForm => !config.formDefs[keyForm].hidden)" :key="keyForm">
        <dynamic-form
          :config="{
                ...config.formDefs[keyForm],
                name: keyForm,
                change: newChange(config.formDefs[keyForm].change),
                displayValue: config.displayValue
              }"
          :baseModel="lineModel"
        ></dynamic-form>
      </v-col>
    </v-row>
    <v-row dense>
      <v-col class="col-btn">
        <v-btn color="green" icon v-if="!config.displayValue">
          <v-icon @click="addItem" :disabled="!bValidForm">mdi-plus-circle</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { formFunctions } from "@/components/form/functions/form";
export default {
  name: "list",
  props: ["config", "baseModel"],
  methods: {
    deleteItem(index) {
      this.baseModel[this.config.name].splice(index, 1);
      this.refresh = !this.refresh;
    },
    addItem() {
      // valid form
      let lineModel = this.config.default || {}
      
      this.baseModel[this.config.name].push(lineModel);
      this.refresh = !this.refresh;
    },
    newChange(oldChange) {
      return ({ $store, config, baseModel }) => {
        this.refresh = !this.refresh;
        oldChange && oldChange({ $store, config, baseModel });
      };
    },
  },
  watch: {
    baseModel: {
      handler() {},
    },
  },
  computed: {
    // TODO mettre ça dans formFunction
    bValidForm() {
      this.refresh;
      if (!this.baseModel[this.config.name]) return true;
      return !this.config.forms.some((keyForm) => {
        const formDef = { ...this.config.formDefs[keyForm], name: keyForm }; // copy ??
        if (
          formDef.condition &&
          !formDef.condition({ baseModel: this.baseModel })
        )
          return false;
        formDef.rules =
          typeof formDef.rules == "function"
            ? formDef.rules({ baseModel: this.baseModel })
            : formDef.rules;
        formFunctions.rules.processRules(formDef);

        return this.baseModel[this.config.name].some((line) => {
          const val = line[formDef.name];
          return (
            formDef.rules && formDef.rules.some((rule) => rule(val) != true)
          );
        });
      });
    },
    lines() {
      this.refresh;
      return this.baseModel[this.config.name];
    },
    configDisplays() {
      return (this.baseModel[this.config.name] || []).map((item) => {
        return {
          ...this.config,
          displayValue: true,
          display: "table",
          value: item,
        };
      });
    },
  },
  components: { dynamicForm: () => import("./dynamic-form") },
  data: () => ({
    configForm: null,
    localModel: {},
    refresh: null,
  }),
  mounted() {
    this.baseModel[this.config.name] = this.baseModel[this.config.name] || [];
  },
};
</script>

<style scoped>
.col-btn {
  max-width: 50px;
}
</style>
