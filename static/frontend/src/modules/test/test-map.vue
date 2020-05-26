<template>
  <div style="width:100%">
    <div v-if="bInit">
      <base-map mapId="map" ref="map" :config="config" fillHeight>
        <div slot="aside" class="map-aside">
          <br />
          <h2>Représentation</h2>
          <list-form
            :baseModel="settings"
            :config="configChoix('color', 'Couleur')"
          ></list-form>
          <list-form
            :baseModel="settings"
            :config="configChoix('icon', 'Icone')"
          ></list-form>
          <h2>Filtres</h2>
          <list-form :config="filterSelect" :baseModel="settings"></list-form>
          <br />
          <div v-for="(filter, index) of filters" :key="index">
            <list-form :config="filter" :baseModel="settings"></list-form>
          </div>
        </div>
      </base-map>
    </div>
  </div>
</template>

<script>
import baseMap from "@/modules/map/base-map.vue";
import listForm from "@/components/form/list-form";
import { restitution } from "@/core/js/restitution";

const items = [
    {
    text: "Dégât",
    name: "degat_types_label",
    split: ", "
  },
  {
    text: "Secteur",
    name: "secteur",
    split: ", "
  },
  {
    text: "Organisme",
    name: "organisme",
    split: ", "
  },
  {
    text: "Type de forêt",
    name: "type_foret",
    split: ", "
  },
  {
    text: "Commune",
    name: "communes",
    split: ", "
  },
  {
    text: "Déclarant",
    name: "declarant",
    split: ", "
  },

  {
    text: "Pâturage",
    name: "b_peuplement_paturage_presence",
    replace: [
      [true, "Oui"],
      [false, "Non"]
    ]
  },
  {
    text: "Protection",
    name: "b_peuplement_protection_existence",
    replace: [
      [true, "Oui"],
      [false, "Non"]
    ]
  },
  {
    text: "Accès au peuplement",
    name: "peuplement_acces_label",
    split: ", "
  },
  {
    text: "Essence principale",
    name: "peuplement_ess_1_label",
    split: ", "
  }
].sort((a, b) => a.text > b.text);

export default {
  name: "testMap",
  data() {
    return {
      filterSelect: {
        display: "autocomplete",
        name: "filters",
        label: "Filtres",
        multiple: true,
        change: () => this.filterSelectChange(),
        returnObject: true,
        items: items
      },
      filters: [],
      settings: {},
      name: "",
      bInit: false,
      declarations: [],
      config: {
        layerList: {
          zc: {},
          aa: {},
          secteurs: {
            zoom: true,
            select: {
              build: true,
              multiple: false,
              display: "autocomplete",
              textFieldName: "label",
              valueFieldName: "id_area",
              zoomOnChange: true,
              returnObject: true,
              change: () => {
                const secteur = this.$refs.map.mapService.baseModel.secteurs;
                this.settings.secteur = secteur ? [secteur.label] : [];
                this.addFilter("secteur");
              }
            }
          }
        }
      }
    };
  },
  methods: {
    addFilter(name) {
      this.settings.filters = this.settings.filters || [];
      if (!this.settings.filters.find(item => item.name == name)) {
        const item = items.find(item => item.name == name);
        console.log(item);
        this.settings.filters.push(item);
        this.filters = [...this.settings.filters];
      }
      console.log("filters", this.settings.filters);

      this.filterSelectChange();
    },
    filterSelectChange() {
      console.log("filterSelectChange", this.settings.filters);

      // filter config
      this.filters = [];
      setTimeout(() => {
        this.filters = this.settings.filters.map(item => {
          const dataList = restitution.dataList(this.declarations, item);
          return {
            name: item.name,
            label: item.text,
            display: "autocomplete",
            multiple: true,
            items: dataList.map(d => d.text),
            // returnObject: true,

            change: () => {
              this.initMarkers();
            }
          };
        });
        this.initMarkers();
      }, 10);

      //
    },

    configChoix(name, label) {
      return {
        name,
        label,
        display: "autocomplete",
        type: "list_form",
        returnObject: true,
        items,
        change: () => {
          this.initMarkers();
        }
      };
    },

    declarationsFiltered() {
      return this.declarations.filter(d => {
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
    },

    initMarkers() {
      // filters
      const colorSetting = this.settings["color"];
      const iconSetting = this.settings["icon"];
      if (!(colorSetting || iconSetting)) {
        this.initMarkersLocalisation();
        if (this.$refs.map) {
          this.$refs.map.mapService._config = this.config;
          this.$refs.map.mapService.initMarkers();
        }
        return;
      }

      this.config.markers = {};
      this.config.markers.declarations = {
        legends: [],
        type: "label",
        coords: "centroid",
        data: this.declarationsFiltered()
      };

      if (colorSetting) {
        this.config.markers.declarations.color = {
          options: {
            ...colorSetting,
            nMax: 7
          }
        };
      }

      if (iconSetting) {
        this.config.markers.declarations.icon = {
          options: {
            ...iconSetting,
            nMax: 7
          }
        };
      }

      this.$refs.map.mapService._config = this.config;
      this.$refs.map.mapService.initMarkers();
    },
    initMarkersLocalisation() {
      delete this.config.markers;
      this.config.markers = {
        declarations: {
          data: this.declarationsFiltered(),
          // type: "circle",
          type: "label",
          coords: "centroid",
          style: {
            color: "blue",
            icon: "circle"
          },
          legends: [
            {
              icon: "circle",
              text: `Localisation des alertes (${
                this.declarationsFiltered().length
              })`,
              color: "blue"
            }
          ]
        }
      };
    }
  },
  components: {
    baseMap,
    listForm
  },
  mounted() {
    this.$store.dispatch("declarations").then(declarations => {
      console.log(declarations[0]);
      this.declarations = declarations;
      this.initMarkers();
      this.bInit = true;
      setTimeout(() => {
        this.settings["filters"] = items.find(
          i => i.text == "b_peuplement_protection_existence"
        );
        this.settings["color"] = items.find(i => i.text == "Commune");
        // this.settings["icon"] = items.find(i => i.text == "Organisme");
        this.settings["icon"] = items.find(i => i.text == "Organisme");
        this.settings = {...this.settings}
        this.initMarkers();
      }, 1000);
    });
  }
};
</script>
