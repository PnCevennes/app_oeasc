<template>
  <div>
    <div v-if="configFormConfiguration">
      <dynamic-form-group
        :config="configFormConfiguration"
        :baseModel="settings"
      ></dynamic-form-group>
      <div class="filters" v-for="(filter, index) of filterForms" :key="index">
        <dynamic-form :config="filter" :baseModel="filters"></dynamic-form>
      </div>
    </div>
  </div>
</template>

<script>
import { restitution } from "./restitution-utils.js";
import dynamicFormGroup from "@/components/form/dynamic-form-group";
import dynamicForm from "@/components/form/dynamic-form";
import configFormConfiguration from "./config/form-restitution.js";
import { copy } from "@/core/js/util/util.js";


export default {
  name: "restitutionConfig",
  props: ["dataType"],
  components: { dynamicFormGroup, dynamicForm },
  data: () => ({
    configRestitution: null,
    filterForms: [],
    settings: {
      display: "map",
      typeGraph: "column",
      nbMax1: 7,
      nbMax2: 7,
      choix1: "degat_gravite",
      choix2: "degat_types_label",
      dataType: "declaration",
      filters: {"degat_types_label": [ "Frottis" ]},
      n:0,
      height: '400px',
    },
    // filters: { secteur: ["Mont Aigoual"] },
    configFormConfiguration: null,
    dataRestitution: null
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

      if(!this.filters) {
        console.log(this.configRestitution.filters)
        this.filters = {...this.settings.filters, ...(this.configRestitution.filters|| {})};
        this.settings.filterList = Object.keys(this.filters);
      }


      for (const formDef of Object.values(configFormConfiguration.formDefs)) {
        formDef.change = () => this.processChoix(); // ideal newChange
      }

      const items = Object.keys(this.configRestitution.items).map(name => ({
        text: this.configRestitution.items[name].text,
        value: name
      }));

      for (const keyForm of ["choix1", "choix2", "filterList"]) {
        configFormConfiguration.formDefs[keyForm].items = items;
      }

      configFormConfiguration.formDefs.filterList.change = this.filterSelectChange;

      this.configFormConfiguration = configFormConfiguration;
      this.filterForms = this.getFilterForms();
      this.processChoix();
    },

    getFilterForms() {
      return this.settings.filterList.map(name => {
        const item = restitution.getItem(name, this.configRestitution);
        const dataList = restitution.dataList(this.dataRestitution, item);
        return {
          type: "list_form",
          name: item.name,
          label: `Filtre : ${item.text}`,
          display: "autocomplete",
          multiple: true,
          items: dataList.map(d => d.text),
          change: () => {
            this.processChoix();
          }
        };
      });
    },

    filterSelectChange() {
      setTimeout(() => {
        this.filterForms = this.getFilterForms();

        for (const key of Object.keys({...this.filters})) {
          if (!this.settings.filterList.includes(key)) {
            delete this.filters[key];
          }
        }
        this.processChoix();
      }, 100);
    },
    getData() {
      this.configRestitution = this.$store.getters.configRestitution(
        this.settings.dataType
      );
      if (!this.configRestitution) {
        return;
      }
      this.$store.dispatch(this.configRestitution.getData).then(data => {
        this.dataRestitution = data;
        console.log(this.dataRestitution.map(d => d.valide))

        this.initConfig();
      });
    },
    processChoix() {
      this.settings.n = this.settings.n + 1; 
      this.$emit("updateSettings", { ...this.settings, filters: copy(this.filters) });
    }
  }
};
</script>
