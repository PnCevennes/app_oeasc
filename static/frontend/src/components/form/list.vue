<template>
  <div>
    <b v-if="!config.displayValue">{{ config.label }}</b>
    <v-row dense v-for="(lineModel, indexLine) of lines" :key="indexLine">
      <v-col v-for="keyForm of config.forms" :key="keyForm">
        <dynamic-form
          :config="{
                ...config.formDefs[keyForm],
                name: keyForm,
                change: newChange(config.formDefs[keyForm].change)
              }"
          :baseModel="lineModel"
        ></dynamic-form>
      </v-col>
      <v-col>
        <v-btn icon color="red" @click="deleteItem(indexLine)">
          <v-icon>mdi-close-circle</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row dense>
      <v-btn color="green" icon>
        <v-icon @click="addItem" :disabled="!bValidForm">mdi-plus-circle</v-icon>
      </v-btn>
    </v-row>
  </div>
</template>

<script>
import { formFunctions } from "@/components/form/functions";
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
      console.log("add Items");
      this.baseModel[this.config.name].push({});
      this.refresh = !this.refresh;
    },
    newChange(oldChange) {
      return ({ $store, config, baseModel }) => {
        this.refresh = !this.refresh;
        oldChange && oldChange({ $store, config, baseModel });
      }
    }
  },
  watch: {
    baseModel: {
      handler() {
        console.log("aaa");
      }
    }
  },
  computed: {
    // TODO mettre ça dans formFunction
    bValidForm() {
      this.refresh;
      if (!this.baseModel[this.config.name]) return true;
      console.log(this.baseModel[this.config.name]);
      return !this.config.forms.some(keyForm => {
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

        console.log(formDef.name, formDef.rules);
        return this.baseModel[this.config.name].some(line => {
          const val = line[formDef.name];
          const cond =
            formDef.rules && formDef.rules.some(rule => rule(val) != true);
          console.log(val, cond);
          return formDef.rules && formDef.rules.some(rule => rule(val) != true);
        });
      });
    },
    lines() {
      this.refresh;
      return this.baseModel[this.config.name];
    },
    configDisplays() {
      return (this.baseModel[this.config.name] || []).map(item => {
        return {
          ...this.config,
          displayValue: true,
          display: "table",
          value: item
        };
      });
    }
  },
  components: { dynamicForm: () => import("./dynamic-form") },
  data: () => ({
    configForm: null,
    localModel: {},
    refresh: null
  }),
  mounted() {
    this.baseModel[this.config.name] = this.baseModel[this.config.name] || [];
    console.log(this.baseModel[this.config.name]);
  }
};
</script>
