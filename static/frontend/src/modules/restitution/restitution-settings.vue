<template>
  <div>
    <div v-if="configFormConfiguration">
      <dynamic-form-group :config="configFormConfiguration" :baseModel="settings"></dynamic-form-group>
      <div class="filters" v-for="(filter, index) of filterForms" :key="index">
        <dynamic-form :config="filter" :baseModel="filters"></dynamic-form>
      </div>
    </div>
  </div>
</template>

<script>
import { restitution } from "./utils.js";
import dynamicFormGroup from "@/components/form/dynamic-form-group";
import dynamicForm from "@/components/form/dynamic-form";
import configFormConfiguration from "./config/form-restitution.js";
import { copy } from "@/core/js/util/util.js";

export default {
  name: "restitution-settings",
  props: ["dataType"],
  components: { dynamicFormGroup, dynamicForm },
  watch: {
    settings: {
      deep: true,
      handler() {
        this.emitSettings();
      },
    },
  },
  data: () => ({
    configRestitution: null,
    filterForms: [],
    settings: {},
    // filters: { secteur: ["Mont Aigoual"] },
    configFormConfiguration: null,
    dataRestitution: null,
  }),
  mounted() {
    this.initConfig();
  },
  methods: {
    initConfig() {
      if (!this.configRestitution) {
        this.getData();
        return;
      }

      if (!this.filters) {
        this.filters = {
          ...this.settings.filters,
          ...(this.configRestitution.filters || {}),
        };
        this.settings.filterList = Object.keys(this.filters);
      }

      for (const formDef of Object.values(configFormConfiguration.formDefs)) {
        formDef.change = () => this.emitSettings(); // ideal newChange
      }

      const items = Object.keys(this.configRestitution.items).map((name) => ({
        text: this.configRestitution.items[name].text,
        value: name,
      }));

      for (const keyForm of ["choix1", "choix2", "filterList"]) {
        configFormConfiguration.formDefs[keyForm].items = items;
      }

      configFormConfiguration.formDefs.filterList.change = this.filterSelectChange;

      this.configFormConfiguration = configFormConfiguration;
      this.filterForms = this.getFilterForms();
      this.emitSettings();
    },

    getFilterForms() {
      return this.settings.filterList.map((name) => {
        const item = restitution.getItem(name, this.configRestitution);
        const dataList = restitution.dataList(this.dataRestitution, item);
        return {
          type: "list_form",
          name: item.name,
          label: `Filtre : ${item.text}`,
          display: "autocomplete",
          multiple: true,
          items: dataList.map((d) => d.text),
          change: () => {
            this.emitSettings();
          },
        };
      });
    },

    filterSelectChange() {
      setTimeout(() => {
        this.filterForms = this.getFilterForms();

        for (const key of Object.keys({ ...this.filters })) {
          if (!this.settings.filterList.includes(key)) {
            delete this.filters[key];
          }
        }
        this.emitSettings();
      }, 100);
    },
    getData() {
      this.configRestitution = this.$store.getters.configRestitution(
        this.dataType
      );
      if (!this.configRestitution) {
        return;
      }

      this.settings = {
        data_type: this.dataType,
        ...(this.configRestitution.default || {}),
      };

      restitution.getData(this.configRestitution, this.$store).then((data) => {
        this.dataRestitution = data;
        this.initConfig();
      });
    },
    emitSettings() {
      this.$emit("updateSettings", {
        ...this.settings,
        filters: copy(this.filters),
        dataType: this.dataType,
      });
    },
  },
};
</script>
