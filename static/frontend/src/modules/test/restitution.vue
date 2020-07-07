<template>
  <div v-if="dataIn">
    <dynamic-form-group
      :config="configFormGroup"
      :baseModel="settings"
    ></dynamic-form-group>

    <!-- <listForm :config="configDisplay" :baseModel="settings"></listForm> -->
    <!-- <div v-if="['map', 'table'].includes(settings.display)">
      <listForm
        :config="configChoix('color', 'Couleur')"
        :baseModel="settings"
      ></listForm>
      <listForm
        :config="configChoix('icon', 'Icône')"
        :baseModel="settings"
      ></listForm>
    </div>
    <div v-if="settings.display == 'graph'">
      <listForm :config="configTypeGraph" :baseModel="settings"></listForm>
      <dynamic
      <listForm
        :config="configChoix('choix1', 'Choix 1')"
        :baseModel="settings"
      ></listForm>
      <listForm
        :config="configChoix('choix2', 'Choix 2')"
        :baseModel="settings"
      ></listForm>
    </div> -->

    <h3>Filtres</h3>
    <list-form :config="filterSelect" :baseModel="settings"></list-form>
    <div class="filters" v-for="(filter, index) of filters" :key="index">
      <list-form :config="filter" :baseModel="settings"></list-form>
    </div>
    <p>
      Nombre total de données filtrées :
      {{ (dataFiltered || []).length }}
      /
      {{ (dataIn || []).length }}
    </p>
  </div>
</template>

<script>
import { restitution } from "@/core/js/restitution";
import dynamicFormGroup from "@/components/form/dynamic-form-group";
import configFormConfiguration from "./config-form-configuration.js";

export default {
  name: "restitution",
  props: ["dataIn", "config"],
  components: { dynamicFormGroup },
  data() {
    return {
      dataFiltered: [],
      filterSelect: {
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
      listChoix: ["color", "icon", "choix1", "choix2"],
      results: {}
    };
  },
  watch: {
    dataIn() {
      this.processChoix();
    }
  },
  mounted() {
    this.settings = {
      display: "graph",
      typeGraph: "pie"
    };
    this.settings.color = this.items().find(item => item.name == "secteur");
    this.settings.icon = this.items().find(item => item.name == "organisme");
    this.settings.choix1 = this.items().find(item => item.name == "secteur");
    this.settings.choix2 = this.items().find(item => item.name == "organisme");
    for (const key of Object.keys(configFormConfiguration)) {
      configFormConfiguration[key].name = key;
      configFormConfiguration[key].change = this.change;
    }
  },
  methods: {
    change() {
      this.processChoix()
    },
    filterSelectChange() {
      this.filters = [];
      setTimeout(() => {
        this.filters = this.settings.filters.map(item => {
          const dataList = restitution.dataList(this.dataIn, item);
          return {
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
      this.dataFiltered = this.getDataFiltered();
      this.results = {
        ...this.settings,
        choix: {}
      };
      for (const name of this.listChoix) {
        if (!this.settings[name]) continue;
        this.results.choix[name] = {
          dataList: restitution.dataList(this.dataFiltered, {
            ...this.settings[name],
            nMax: 7 // TODO
          }),
          text: this.settings[name].text,
          name: this.settings[name].name
        };
      }
      this.results.markers = this.markers();
      this.results.markerLegendGroups = this.markerLegendGroups();

      this.$emit("updateResults", this.results);
    },

    markers() {
      return this.dataFiltered.map(data => {
        const icon =
          this.settings.icon &&
          restitution.valueOfType(
            "icon",
            data[this.settings.icon.name],
            this.results.choix.icon.dataList,
            this.settings.icon
          );
        const color =
          this.settings.color &&
          restitution.valueOfType(
            "color",
            data[this.settings.color.name],
            this.results.choix.color.dataList,
            this.settings.color
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
        this.results.choix.color &&
        this.results.choix.icon &&
        this.results.choix.icon.name == this.results.choix.color.name;
      console.log(
        cond_same,
        this.results.choix.icon,
        this.results.choix.color.name
      );
      for (const [name, res] of Object.entries(this.results.choix || {})) {
        const markerLegends = {
          title: res.text,
          legends: res.dataList.map(data => ({
            text: data.text,
            count: data.count,
            icon: ((cond_same || name == "icon") && data.icon) || icon_default,
            color:
              ((cond_same || name == "color") && data.color) || color_default
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
