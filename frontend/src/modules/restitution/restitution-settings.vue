<template>
  <div>
    <div v-if="configFormRestition">
      <dynamic-form-group
        :config="configFormRestition"
        :baseModel="settings"
      ></dynamic-form-group>
      <div class="filters" v-for="filter of filterForms" :key="filter.name">
        <dynamic-form
          :config="filter"
          :baseModel="settings.filters"
        ></dynamic-form>
      </div>
    </div>
  </div>
</template>

<script>
import { Restitution } from "./restitution.js";
import dynamicFormGroup from "@/components/form/dynamic-form-group";
import dynamicForm from "@/components/form/dynamic-form";
import configFormRestition from "./config/form-restitution.js";

export default {
  name: "restitution-settings",
  components: { dynamicFormGroup, dynamicForm },
  props: ["dataType"],
  watch: {
    settings: {
      deep: true,
      handler() {
        this.emitSettings();
      }
    }
  },
  data: () => ({
    filterForms: [],
    settings: {},
    configFormRestition: null,
    restitution: null,
    n: 0
  }),
  mounted() {
    this.initConfig();
  },
  methods: {
    initRestitution() {
      this.restitution = new Restitution(
        this.settings.dataType || this.dataType,
        this.$store
      );
      this.restitution.getConfig();
      this.restitution.getData().then(() => {
        this.settings = this.restitution.options();
        if (!this.filters) {
          this.filters = {
            ...this.settings.filters,
            ...(this.restitution.options.filters || {})
          };
          this.settings.filterList = Object.keys(this.filters);
        }
        this.initConfig();
      });
    },
    initConfig() {
      if (!this.restitution) {
        this.initRestitution();
        return;
      }

      this.restitution.setOptions(this.options());

      configFormRestition.formDefs.groupByKey.items = this.restitution.options().groupByKeyItems;
      for (const formDef of Object.values(configFormRestition.formDefs)) {
        formDef.change = () => {
          this.emitSettings()
        }; // ideal newChange
      }

      const items = Object.keys(this.restitution.items)
      .filter(name => this.restitution.items[name].text)
      .map(name => ({
        text: this.restitution.items[name].text,
        value: name
      }));

      for (const keyForm of ["choix1", "choix2", "filterList"]) {
        configFormRestition.formDefs[keyForm].items = items;
      }

      configFormRestition.formDefs.filterList.change = this.filterSelectChange;

      this.configFormRestition = configFormRestition;
      this.filterForms = this.getFilterForms();
      this.emitSettings();
    },

    getFilterForms() {
      return this.settings.filterList.map(name => {
        const item = this.restitution.item(name);
        const dataList = this.restitution.dataList(name, {});
        return {
          type: "list_form",
          name: item.key,
          label: `Filtre : ${item.text}`,
          display: "autocomplete",
          multiple: true,
          items: dataList.map(d => d.text),
          change: () => {
            this.filterFormsChange();
          }
        };
      });
    },

    filterFormsChange() {
      this.n = this.n + 1;
      this.emitSettings();
    },

    filterSelectChange() {
      this.filterForms = this.getFilterForms();
      this.n = this.n + 1;
      for (const key of Object.keys({ ...this.settings.filters })) {
        if (!this.settings.filterList.includes(key)) {
          delete this.settings.filters[key];
        }
      }
      setTimeout(() => {
        this.emitSettings();
      }, 100);
    },
    options() {
      return {
        ...this.settings
      };
    },
    emitSettings() {
      
      // this.n = this.n+1;
  
      const settings = this.options();
      settings.n = this.n;

      this.$emit("updateSettings", settings);
    }
  }
};
</script>
