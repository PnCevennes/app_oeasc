<template>
<div>
  <div v-if="dataIn && configFormConfiguration">
    <dynamic-form-group :config="configFormConfiguration" :baseModel="settings"></dynamic-form-group>

    <h3>Filtres</h3>
    <dynamic-form :config="filterSelect" :baseModel="settings"></dynamic-form>
    <div class="filters" v-for="(filter, index) of filters" :key="index">
      <dynamic-form :config="filter" :baseModel="settings"></dynamic-form>
    </div>
    <p>
      Nombre total de données filtrées :
      {{ (dataFiltered || []).length }}
      /
      {{ (dataIn || []).length }}
    </p>
  </div>
</div>
</template>

<script>
import { restitution } from "./restitution.js";
import dynamicFormGroup from "@/components/form/dynamic-form-group";
import dynamicForm from "@/components/form/dynamic-form";
import configFormConfiguration from "./config/form-configuration.js";

export default {
  name: "restitution",
  props: ["dataIn", "config"],
  components: { dynamicFormGroup, dynamicForm },
  data() {
    return {
      dataFiltered: [],
      filterSelect: {
        type: "list_form",
        display: "autocomplete",
        name: "filters",
        label: "Filtres",
        multiple: true,
        change: () => this.filterSelectChange(),
        returnObject: true,
        items: this.items()
      },
      filters: [],
      settings: {},
      listChoix: ["choix1", "choix2"],
      results: {},
      configFormConfiguration: null
    };
  },
  watch: {
    dataIn() {
      this.processChoix();
    }
  },
  mounted() {
    this.initConfig();
  },
  methods: {
    initConfig() {
      this.settings = {
        // display: "table",
        // display: "graph",
        display: "map",
        typeGraph: "column",
        nMax1: 7,
        nMax2: 7
      };
      this.settings.choix1 = this.items().find(
        item => item.name == "organisme"
      );
      this.settings.choix2 = this.items().find(
        item => item.name == "degat_types_label"
      );


      for (const formDef of Object.values(configFormConfiguration.formDefs)) {
        formDef.change = this.change; // ideal newChange
      }

      for (const keyForm of ["choix1", "choix2"]) {
        console.log(keyForm, configFormConfiguration.formDefs[keyForm])
        configFormConfiguration.formDefs[keyForm].items = this.items();
      }

      console.log(configFormConfiguration)

      this.configFormConfiguration = configFormConfiguration;
    },
    change() {
      this.processChoix();
    },
    filterSelectChange() {
      this.filters = [];
      setTimeout(() => {
        this.filters = this.settings.filters.map(item => {
          const dataList = restitution.dataList(this.dataIn, item);
          return {
            type: "list_form",
            name: item.name,
            label: item.text,
            display: "autocomplete",
            multiple: true,
            items: dataList.map(d => d.text),
            change: () => {
              this.processChoix();
            }
          };
        });
        this.processChoix();
      }, 10);
    },

    items(name) {
      let items = Object.keys(this.config.items).map(key => ({
        ...this.config.items[key],
        name: key
      }));
      if (this.config[name]) {
        items = items.filter(item => this.config[name].includes(item.name));
      }
      return items;
    },

    processChoix() {
      console.log("processChoix", this.settings);
      this.dataFiltered = this.getDataFiltered();
      this.results = {
        ...this.settings,
        choix: {}
      };

      this.results.choix.choix1 = {
        dataList:
          this.settings.choix1 && this.settings.choix2
            ? restitution.dataList2(
                this.dataFiltered,
                {
                  ...this.settings.choix1,
                  nMax: this.settings.nMax1
                },
                {
                  ...this.settings.choix2,
                  nMax: this.settings.nMax2
                }
              )
            : restitution.dataList(this.dataFiltered, {
                ...this.settings.choix1,
                nMax: this.settings.nMax1
              }),
        text: this.settings.choix1.text,
        name: this.settings.choix1.name
      };
      this.results.choix.choix2 = this.settings.choix2 && {
        dataList: restitution.dataList(this.dataFiltered, {
          ...this.settings.choix2,
          nMax: this.settings.nMax2
        }),
        text: this.settings.choix2.text,
        name: this.settings.choix2.name
      };

      this.results.markers = this.markers();
      this.results.markerLegendGroups = this.markerLegendGroups();

      this.$emit("updateResults", this.results);
    },

    markers() {
      return this.dataFiltered.map(data => {
        const icon =
          this.settings.choix2 &&
          restitution.valueOfType(
            "icon",
            data[this.settings.choix2.name],
            this.results.choix.choix2.dataList,
            {
              ...this.settings.choix2,
              filters: this.settings
            }
          );
        const color =
          this.settings.choix1 &&
          restitution.valueOfType(
            "color",
            data[this.settings.choix1.name],
            this.results.choix.choix1.dataList,
            {
              ...this.settings.choix1,
              filters: this.settings
            }
          );
        return {
          coords: data[this.config.coordsFieldName],
          type: "label",
          style: {
            icon,
            color
          }
        };
      });
    },

    markerLegendGroups() {
      const icon_default = "circle";
      const color_default = "rgb(150,150,150)";
      const markerLegendGroups = [];
      const cond_same =
        this.results.choix.choix1 &&
        this.results.choix.choix2 &&
        this.results.choix.choix2.name == this.results.choix.choix1.name;

      for (const [name, res] of Object.entries(this.results.choix || {})) {
        if (!["choix1", "choix2"].includes(name) || !res) {
          continue;
        }
        const markerLegends = {
          title: res.text,
          legends: res.dataList
            .filter(
              data =>
                !this.settings[res.name] ||
                !this.settings[res.name].length ||
                this.settings[res.name].includes(data.text)
            )
            .map(data => ({
              text: data.text,
              count: data.count,
              icon:
                ((cond_same || name == "choix2") && data.icon) || icon_default,
              color:
                ((cond_same || name == "choix1") && data.color) || color_default
            }))
        };

        markerLegendGroups.push(markerLegends);

        if (cond_same) break;
      }
      return markerLegendGroups;
    },

    getDataFiltered() {
      const dataFiltered = this.dataIn.filter(d => {
        let cond = true;
        for (const filter of this.filters) {
          const name = filter.name;
          const options = this.settings.filters.find(item => item.name == name);
          const value = restitution.getValue(d[name], options);
          const test = this.settings[name];
          if (!test) continue;
          const condFilter =
            (test || []).filter(v => {
              return value.includes(v);
            }).length > 0 || test.length == 0;
          cond = cond && condFilter;
        }
        return cond;
      });
      return dataFiltered;
    }
  }
};
</script>
