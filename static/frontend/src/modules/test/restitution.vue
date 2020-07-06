<template>
  <div v-if="dataIn">
    <listForm :config="configDisplay" :baseModel="settings"></listForm>

    <h3>Choix</h3>
    <listForm
      :config="configChoix('color', 'Couleur')"
      :baseModel="settings"
    ></listForm>
    <listForm
      :config="configChoix('icon', 'Icône')"
      :baseModel="settings"
    ></listForm>
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
import listForm from "@/components/form/list-form";

export default {
  name: "restitution",
  props: ["dataIn", "config"],
  components: { listForm },
  data() {
    return {
      configDisplay: {
        name: "display",
        display: "button",
        label: "Affichage",
        items: [
          { value: "table", text: "Tableau" },
          { value: "map", text: "Carte" },
          { value: "graph", text: "Graphique" }
        ],
        change: () => {
          this.processChoix();
        }
      },
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
      settings: {
        display: "graph",
        color: {
          text: "Secteur",
          split: ", ",
          color: {
            "Causses et Gorges": "#e8e805",
            "Mont Aigoual": "red",
            "Mont Lozère": "blue",
            "Vallées cévenoles": "green"
          },
          name: "secteur"
        },
        icon: { text: "Organisme", name: "organisme", split: ", " }
      },
      listChoix: ["color", "icon"],
      results: {}
    };
  },
  watch: {
    dataIn() {
      this.processChoix();
    }
  },
  methods: {
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

    configChoix(name, label) {
      return {
        name,
        label,
        display: "autocomplete",
        type: "list_form",
        returnObject: true,
        items: this.items(name),
        change: () => {
          this.processChoix();
        }
      };
    },

    processChoix() {
      this.dataFiltered = this.getDataFiltered();
      this.results = {
        display: this.settings.display,
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
          name: this.settings[name].name,
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
      const icon_default = 'circle';
      const color_default = 'rgb(150,150,150)';
      const markerLegendGroups = [];
      const cond_same =
        this.results.choix.color &&
        this.results.choix.icon &&
        this.results.choix.icon.name == this.results.choix.color.name;
      console.log(cond_same, this.results.choix.icon, this.results.choix.color.name)
      for (const [name, res] of Object.entries(this.results.choix || {})) {
        const markerLegends = {
          title: res.text,
          legends: res.dataList.map((data) =>({
            text: data.text,
            count: data.count,
            icon: (cond_same || name == 'icon')  && data.icon || icon_default,
            color: (cond_same || name == 'color')  && data.color || color_default,
          }))
        };
        markerLegendGroups.push(markerLegends);

        if(cond_same) break;
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
