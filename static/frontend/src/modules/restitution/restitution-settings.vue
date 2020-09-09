<template>
  <div>
<<<<<<< HEAD
    <div v-if="configFormRestition">
      <dynamic-form-group :config="configFormRestition" :baseModel="settings"></dynamic-form-group>
      <div class="filters" v-for="filter of filterForms" :key="filter.name">
        <dynamic-form :config="filter" :baseModel="settings.filters"></dynamic-form>
=======
    <div v-if="configFormConfiguration">
      <dynamic-form-group
        :config="configFormConfiguration"
        :baseModel="settings"
      ></dynamic-form-group>
      <div class="filters" v-for="(filter, index) of filterForms" :key="index">
        <dynamic-form :config="filter" :baseModel="filters"></dynamic-form>
>>>>>>> f6d382343a4a09fc85582a5f8320f20e91b54364
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
<<<<<<< HEAD
    configFormRestition: null,
    restitution: null,
=======
    // filters: { secteur: ["Mont Aigoual"] },
    configFormConfiguration: null,
    dataRestitution: null
>>>>>>> f6d382343a4a09fc85582a5f8320f20e91b54364
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
            ...(this.restitution.options.filters || {}),
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

<<<<<<< HEAD
      this.restitution.setOptions(this.options());

      for (const formDef of Object.values(configFormRestition.formDefs)) {
        formDef.change = () => this.emitSettings(); // ideal newChange
      }

      const items = Object.keys(this.restitution.items).map((name) => ({
        text: this.restitution.items[name].text,
        value: name,
      }));
=======
      if (!this.filters) {
        this.filters = {
          ...this.settings.filters,
          ...(this.configRestitution.filters || {})
        };
        this.settings.filterList = Object.keys(this.filters);
      }

      for (const formDef of Object.values(
        configFormConfiguration.formDefs
      )) {
        formDef.change = () => this.emitSettings(); // ideal newChange
      }

      let items = Object.keys(this.configRestitution.items)
        .map(name => ({
          text: this.configRestitution.items[name].text,
          value: name
        }))
        items = items.sort((a, b) => 
          a.text < b.text ? -1 : 1
        );
>>>>>>> f6d382343a4a09fc85582a5f8320f20e91b54364

      console.log(items.map(a=>a.text))
      for (const keyForm of ["choix1", "choix2", "filterList"]) {
        configFormRestition.formDefs[keyForm].items = items;
      }

      configFormRestition.formDefs.filterList.change = this.filterSelectChange;

      this.configFormRestition = configFormRestition;
      this.filterForms = this.getFilterForms();
      this.emitSettings();
    },

    getFilterForms() {
<<<<<<< HEAD
      return this.settings.filterList.map((name) => {
        const item = this.restitution.item(name);
        const dataList = this.restitution.dataList(name, {});
=======
      return this.settings.filterList.map(name => {
        const item = restitution.getItem(name, this.configRestitution);
        const dataList = restitution.dataList(this.dataRestitution, item);
>>>>>>> f6d382343a4a09fc85582a5f8320f20e91b54364
        return {
          type: "list_form",
          name: item.key,
          label: `Filtre : ${item.text}`,
          display: "autocomplete",
          multiple: true,
          items: dataList.map(d => d.text),
          change: () => {
            this.emitSettings();
          }
        };
      });
    },

    filterSelectChange() {
      this.filterforms={};
      setTimeout(() => {
        this.filterForms = this.getFilterForms();

        for (const key of Object.keys({ ...this.settings.filters })) {
          if (!this.settings.filterList.includes(key)) {
            delete this.settings.filters[key];
          }
        }
        this.emitSettings();
      }, 10);
    },
<<<<<<< HEAD
    options() {
      return {
        ...this.settings,
      };
    },
    emitSettings() {
      this.$emit("updateSettings", this.options());
    },
  },
=======
    getData() {
      this.configRestitution = this.$store.getters.configRestitution(
        this.dataType
      );
      if (!this.configRestitution) {
        return;
      }

      this.settings = {
        data_type: this.dataType,
        ...(this.configRestitution.default || {})
      };

      restitution.getData(this.configRestitution, this.$store).then(data => {
        this.dataRestitution = data;
        this.initConfig();
      });
    },
    emitSettings() {
      this.$emit("updateSettings", {
        ...this.settings,
        filters: copy(this.filters),
        dataType: this.dataType
      });
    }
  }
>>>>>>> f6d382343a4a09fc85582a5f8320f20e91b54364
};
</script>
