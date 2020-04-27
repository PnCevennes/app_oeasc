<template>
  <div style="width:100%">
    <div v-if="bInit">
      <base-map mapId="map" ref="map" :config="config" fillHeight>
        <div slot="aside" class="map-aside">
          <list-form
            :baseModel="settings"
            :config="configChoix('color', 'Couleur')"
          ></list-form>
          <list-form
            :baseModel="settings"
            :config="configChoix('icon', 'Icone')"
          ></list-form>
        </div>
      </base-map>
    </div>
  </div>
</template>

<script>
import baseMap from "@/modules/map/base-map.vue";
import listForm from "@/components/form/list-form";

const items1 = [
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
];

const items = items1.sort((a, b) => a.text > b.text);

export default {
  name: "testMap",
  data() {
    return {
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
              markerFilter: {
                markerFieldName: "areas_localisation_raw"
              }
            }
          }
        }
      }
    };
  },
  methods: {
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

    initMarkers() {
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
        data: this.declarations
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
          data: this.declarations,
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
              text: "Localisation des alertes",
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
        // this.settings["color"] = items.find(i => i.text == "Organisme");
        // this.settings["icon"] = items.find(i => i.text == "Organisme");
        // this.settings["icon"] = items.find(i => i.text == "Type de forêt");
        // this.initMarkers();
      }, 1000);
    });
  }
};
</script>
