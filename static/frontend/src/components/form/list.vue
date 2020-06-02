<template>
  <v-form v-model="bValidForm" ref="form" v-if="config">
    <b v-if="!config.displayValue">{{ config.label }}</b>
    <v-simple-table>
      <thead>
        <template v-for="[name, form] of Object.entries(config.forms)">
          <th v-if="form.hidden" :key="name">
            {{ form.label }}
          </th>
        </template>
        <th v-if="!config.displayValue">Action</th>
      </thead>
      <tbody>
        <tr v-for="(model, index) of baseModel[config.name]" :key="index">
          <td v-for="[name, form] of Object.entries(config.forms)" :key="name">
            <dynamic-form
              :config="{
                ...form,
                name,
                displayValue: true,
                displayLabel: false
              }"
              :baseModel="model"
            ></dynamic-form>
          </td>
          <td v-if="!config.displayValue">
            <v-btn icon color="red" @click="deleteItem(index)"
              ><v-icon>mdi-close-circle</v-icon></v-btn
            >
          </td>
        </tr>
        <tr v-if="localModel && !config.displayValue">
          <td v-for="[name, form] of Object.entries(config.forms)" :key="name">
            <dynamic-form
              :config="{ ...form, name }"
              :baseModel="localModel"
            ></dynamic-form>
          </td>
          <td v-if="!config.displayValue">
            <v-btn icon color="green" @click="addItem()"
              ><v-icon>mdi-plus-circle</v-icon></v-btn
            >
          </td>
        </tr>
      </tbody>
    </v-simple-table>
  </v-form>
</template>

<script>
import { copy } from "@/core/js/util/util";
export default {
  name: "list",
  props: ["config", "baseModel"],
  methods: {
    deleteItem(index) {
      this.baseModel[this.config.name].splice(index, 1);
    },
    addItem() {
      // valid form
      if (this.$refs.form.validate()) {
        this.baseModel[this.config.name].push(copy(this.localModel));
        this.localModel = null;
        setTimeout(() => {
          this.localModel = {};
        }, 100);
      }
    }
  },
  computed: {
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
    bValidForm: false
  }),
  mounted() {
    this.baseModel[this.config.name] = this.baseModel[this.config.name] || [];
  }
};
</script>
